from typing import TYPE_CHECKING

from flask.app import Flask
from flask_jwt_extended.exceptions import CSRFError, NoAuthorizationError
from flask_jwt_extended.jwt_manager import JWTManager
from flask_principal import (
    Identity,
    Need,
    PermissionDenied,
    RoleNeed,
    UserNeed,
    identity_changed,
    identity_loaded,
)

from app.apis.v1.app_logging.models import ErrorLog
from app.exceptions import InvalidUsage
from app.utils import g
from app.utils.custom_principal_needs import OrganizationNeed
from app.utils.helpers import get_user_entity_permissions

if TYPE_CHECKING:
    from app.apis.v1.users.models import User


def on_identity_loaded(sender, identity: int):

    pass


def generate_principal_identity(user: "User"):

    user_id = user.id
    identity = Identity(user_id)
    identity.provides.add(UserNeed(user_id))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    for role in user.roles:
        identity.provides.add(RoleNeed(role.name))

    # gets entity permissions granted to user or user's roles and add valid permissions
    entity_permissions = get_user_entity_permissions(user_id)

    for entity in entity_permissions:
        for permission in [
            Need(entity.entity_name, perm)
            for perm in ["create", "edit"]
            if getattr(entity, perm)
        ]:
            identity.provides.add(permission)

    identity.provides.add(OrganizationNeed(user.affiliation.organization.name))

    return identity


def jwt_handlers(jwt: JWTManager, app: Flask):
    def user_identity_lookup(user: "User"):
        return user.id

    def user_lookup_callback(_jwt_header, jwt_data):

        from app.apis.v1.users.models import Session, User

        session = Session.get(token=jwt_data["jti"], user_id=jwt_data["user"])
        g.session = session
        if not session:
            raise InvalidUsage.invalid_session()
        user_id = jwt_data["user"]
        user = User.get(id=user_id)
        if not user or not user.active:
            raise InvalidUsage.user_not_authorized()

        identity = generate_principal_identity(user)
        identity_changed.send(app, identity=identity)

        return user

    def invalid_token_loader_callback(*args):

        return InvalidUsage.wrong_login_creds().to_json()

    jwt.user_identity_loader(user_identity_lookup)

    jwt.user_lookup_loader(user_lookup_callback)

    jwt.invalid_token_loader(invalid_token_loader_callback)


def invalid_error_handler(e: InvalidUsage):
    return e.to_json()


def invalid_csrf(e: CSRFError):
    return InvalidUsage.custom_error("Please log-in first.", 402).to_json()


def permission_denied(e: PermissionDenied):
    return InvalidUsage.user_not_authorized().to_json()


def normalize_errors(e: Exception):
    error_log = ErrorLog(e)

    from app.database import db

    db.session.rollback()

    error_log.save(True)

    return InvalidUsage.custom_error(
        getattr(
            e, "msg", getattr(e, "error", getattr(e, "message", "Undefined error"))
        ),
        code=getattr(e, "code", 404),
    ).to_json()


def register_handlers(app: Flask) -> Flask:
    """A function to register global request handlers.
    To register a handler add them like the example
    Example usage:

        def fn(request: Request):
            pass

        app.before_request(fn)

    Args:
        app (Flask): Flask Application instance

    Returns:
        Flask: Flask Application instance
    """
    identity_loaded.connect_via(app)(on_identity_loaded)

    app.errorhandler(PermissionDenied)(permission_denied)
    app.errorhandler(CSRFError)(invalid_csrf)
    app.errorhandler(NoAuthorizationError)(invalid_csrf)
    app.errorhandler(InvalidUsage)(invalid_error_handler)
    app.errorhandler(Exception)(normalize_errors)

    return app
