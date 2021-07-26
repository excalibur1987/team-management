from typing import Dict, List

import werkzeug
from flask import jsonify, request
from flask.helpers import make_response
from flask.wrappers import Response
from flask_jwt_extended import current_user, jwt_required
from flask_jwt_extended.exceptions import CSRFError
from flask_jwt_extended.utils import (
    create_access_token,
    get_csrf_token,
    get_jti,
    get_jwt,
    set_access_cookies,
    unset_jwt_cookies,
)
from flask_jwt_extended.view_decorators import verify_jwt_in_request
from flask_principal import Permission, RoleNeed
from flask_restx import Resource, marshal
from flask_restx.reqparse import RequestParser
from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.functions import func

from app.apis.v1.organization.models import Organization, OrganizationDepartment
from app.apis.v1.organization.parsers import department_parser, organization_parser
from app.database import db
from app.exceptions import InvalidUsage, UserExceptions
from app.settings import Config
from app.utils import g
from app.utils.decorators import has_roles
from app.utils.file_handler import FileHandler
from app.utils.helpers import combine_parsers
from app.utils.parsers import offset_parser

from ..roles.models import Role
from .api_models import session_model, user_model
from .models import Session, User, UserAffiliation
from .namespace import api
from .parsers import user_info_parser, user_login_parser, user_parser
from .utils import extract_request_info

current_user: "User"


class UsersResource(Resource):
    active_users_parser = RequestParser()
    active_users_parser.add_argument(
        "active", type=int, choices=[0, 1], location="args", default=1
    )

    @jwt_required()
    @has_roles("admin")
    @api.doc("get list of users")
    @api.expect(combine_parsers(active_users_parser, offset_parser))
    @api.serialize_multi(user_model, User, description="List of users")
    def get(
        self,
    ):
        """Gets list of users"""

        args = self.active_users_parser.parse_args()

        return User.query.filter(User.active == bool(args.get("active", 1))).all()


class UserSignupResource(Resource):
    user_signup_parser = user_parser.copy().add_argument(
        "position",
        type=str,
        choices=[str(item) for item in Config.VALID_POSITIONS.items],
        location="form",
    )

    @api.doc("Create new user")
    @api.marshal_with(user_model)
    @api.expect(
        combine_parsers(
            user_signup_parser,
            organization_parser,
            department_parser,
        )
    )
    def post(self):
        """Creates new user - requires admin permission-."""
        organization_args: dict = dict(
            (k.replace("organization_", ""), v)
            for (k, v) in organization_parser.parse_args().items()
        )
        user_args: dict = self.user_signup_parser.parse_args()
        user_position = user_args.pop("position")
        department_args: dict = dict(
            (k.replace("dep_", ""), v)
            for (k, v) in department_parser.parse_args().items()
        )

        use_user_info = organization_args.pop("my_info", False)
        if use_user_info:
            organization_args.update(
                {"email": user_args.get("email"), "phone": user_args.get("phone")}
            )

        if (
            Organization.query.filter(
                func.lower(Organization.name)
                == organization_args.get("name", "").lower()
            ).count()
            > 0
        ):
            raise InvalidUsage.custom_error(
                "Organization already registered, kindly "
                + "contact responsible person to send you an invitation",
                401,
            )
        photo: werkzeug.datastructures.FileStorage = user_args.pop("photo")

        if photo:
            photostorage = FileHandler(data=photo.stream, title=photo.filename)
            user_args["photo"] = photostorage
        user = User(**user_args)
        user.save()
        user.add_roles(Role.get(name="user"))
        db.session.flush()

        organization = Organization(**organization_args, contact_user_id=user.id)
        organization.save()
        db.session.flush()

        if len([val for val in department_args.values() if val is not None]) > 0:
            if user_position.lower() == "ceo":
                raise InvalidUsage.custom_error(
                    "CEO can only be specified with no department", 401
                )

            department = OrganizationDepartment(**department_args, org=organization)
            department.save()
            db.session.flush()
        else:
            department = None

        affiliation = UserAffiliation(
            user=user, org=organization, position=user_position, org_dep=department
        )
        affiliation.save()
        db.session.commit()

        photostorage.save()
        return user


@api.param("user_id", "user's id", type=int)
class UserResource(Resource):
    @jwt_required()
    @api.doc("get user's info by id, or list of users")
    @api.response(200, "user info model", model=user_model)
    @api.marshal_with(user_model)
    def get(self, user_id: int = None):
        """Gets user's info"""
        user = User.get(id=user_id)

        return user

    @jwt_required()
    @api.doc("update user's info")
    @api.marshal_with(user_model)
    @api.expect(user_info_parser)
    def put(self, user_id: int = None):
        """Updates user's info"""
        if user_id != current_user.id:
            raise InvalidUsage.user_not_authorized()
        args: Dict = user_info_parser.parse_args()

        newpwd = args.pop("password")
        pwdcheck = args.pop("password_check")

        if newpwd:
            if newpwd != pwdcheck:
                raise UserExceptions.password_check_invalid()
            current_user.password = newpwd

        photo: werkzeug.datastructures.FileStorage = args.pop("photo")

        if photo:
            photostorage = FileHandler(
                data=photo.stream, title=photo.filename, url=current_user._photo
            )
            photostorage.save()
            current_user.photo = photostorage

        for key, val in args.items():
            if hasattr(current_user, key) and val is not None:
                setattr(current_user, key, val)

        db.session.commit()

        return current_user

    @jwt_required()
    @api.doc("delete user's own account")
    @api.expect(
        user_login_parser.copy()
        .replace_argument(
            "username", required=True, location="form", help="You must provide username"
        )
        .add_argument(
            "confirm",
            type=bool,
            required=True,
            help="You must confirm deletion",
            location="form",
        )
    )
    def delete(self, user_id: int = None):
        """Deletes user's account permenantly"""
        args = user_login_parser.parse_args()
        user = User.get(id=user_id)

        if user_id != current_user.id:
            if g.identity.can(Permission(RoleNeed("admin"))):
                return self.admin_delete_user(user)
            raise InvalidUsage.user_not_authorized()
        if (
            user.username != args.get("username", None)
            or user.password != args.get("password", None)
            or not args.get("confirm", False)
        ):
            raise UserExceptions.wrong_login_creds()
        user.delete()
        response: Response = jsonify({"message": "User Account deleted succefully!"})
        unset_jwt_cookies(response)
        return response

    def admin_delete_user(self, user: User):
        user.delete()

        return {}


class LogoutResource(Resource):
    @api.doc("logout user and invalidate session")
    def get(self):
        try:
            verify_jwt_in_request()
            active_session_token = get_jwt()["jti"]

            Session.get(token=active_session_token).update(
                active=False, ignore_none=True, persist=True
            )
        except CSRFError:
            pass
        response: Response = jsonify({"message": "User logged out!"})
        response.delete_cookie("csrftoken")
        unset_jwt_cookies(response)

        return response


class LoginResource(Resource):
    @api.doc("login user")
    @api.response(200, "Successful login", model=user_model)
    @api.response(404, "Invalid url")
    @api.expect(user_login_parser)
    def post(self):
        """User's login view"""
        args = user_login_parser.parse_args()
        user: User = User.query.filter(
            or_(
                func.lower(User.email) == args.get("username", "").lower(),
                func.lower(User.username) == args.get("username", "").lower(),
            )
        ).first()

        if not user or user.password != args.get("password", None):
            raise UserExceptions.wrong_login_creds()
        token = create_access_token(user)
        user.token = get_csrf_token(token)
        user_session = Session(
            user=user, token=get_jti(token), **extract_request_info(request=request)
        )
        user_session.save(True)
        response = make_response(
            marshal(
                user,
                user_model,
            )
        )
        set_access_cookies(response=response, encoded_access_token=token)
        return response


@api.param("user_id", "user's id", type=int)
@api.param("slug", "session's slug", type=str)
class UserSession(Resource):
    @jwt_required()
    @api.response(200, "User session", model=session_model)
    @api.marshal_with(session_model)
    def get(self, user_id: int, slug: str):
        if current_user.id != user_id and not g.identity.provides(RoleNeed("admin")):
            raise InvalidUsage.user_not_authorized()
        return Session.get(slug=slug, user_id=user_id)

    @jwt_required()
    @api.marshal_with(session_model)
    def delete(self, user_id: int, slug: str):
        if current_user.id != user_id and not g.identity.provides(RoleNeed("admin")):
            raise InvalidUsage.user_not_authorized()
        user_session = Session.get(slug=slug, user_id=user_id)
        user_session.delete(True)

        return


@api.param("user_id", "user's id", type=int)
class UserSessions(Resource):
    @jwt_required()
    @api.expect(offset_parser)
    @api.serialize_multi(session_model, Session, description="User's Active Sessions")
    def get(self, user_id: int = None):
        """Gets a list of user's active sessions"""
        args = offset_parser.parse_args()

        user_sessions = (
            Session.query.filter(
                Session.user_id == user_id,
            )
            .order_by(Session.id.asc())
            .offset(args.get("offset", 0))
            .limit(args.get("limit", 10))
            .all()
        )

        return user_sessions

    @jwt_required()
    @api.serialize_multi(session_model, Session, description="User's Active Sessions")
    def delete(self, user_id: int = None, slug: str = None):
        """Invalidates all users sessions except the current sessions"""
        user = User.get(id=user_id)

        if user.id != current_user.id and not g.identity.provides(RoleNeed("admin")):
            raise UserExceptions.wrong_login_creds()

        active_session_token = get_jwt()["jti"]

        user_sessions: List[Session] = Session.query.filter(
            Session.user_id == user.id
        ).all()
        for session_ in user_sessions:
            if session_.token != active_session_token:
                session_.delete(True)
        return [
            session_
            for session_ in user_sessions
            if session_.token == active_session_token
        ]


class UserInvitationResource(Resource):
    @api.marshal_with(user_invitation_model)
    def get(self, slug: str):

        return UserInvitation.get(slug=slug)

    @api.expect(user_parser)
    @api.response(200, "Valid signup", model=user_model)
    def post(self, slug: str):

        invitation = UserInvitation.get(slug=slug)

        user_args = user_parser.parse_args()

        photo: werkzeug.datastructures.FileStorage = user_args.pop("photo")

        if photo:
            photostorage = FileHandler(data=photo.stream, title=photo.filename)
            user_args["photo"] = photostorage
        user = User(**user_args)
        user.save()
        user.add_roles(Role.get(name="user"))
        db.session.flush()

        affiliation = UserAffiliation(
            user=user,
            org=invitation.organization,
            position=invitation.position,
            org_dep=invitation.department,
        )
        affiliation.save()
        db.session.commit()

        photostorage.save()

        token = create_access_token(user)
        user.token = get_csrf_token(token)
        user_session = Session(
            user=user, token=get_jti(token), **extract_request_info(request=request)
        )
        user_session.save(True)
        response = make_response(
            marshal(
                user,
                user_model,
            )
        )
        set_access_cookies(response=response, encoded_access_token=token)
        return response
