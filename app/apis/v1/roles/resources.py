from typing import List

from flask_jwt_extended import jwt_required
from flask_restx import Resource, fields
from flask_restx.errors import abort
from flask_restx.reqparse import RequestParser

from app.database import db
from app.exceptions import InvalidUsage
from app.utils.decorators import has_roles
from app.utils.extended_objects import ExtendedNameSpace
from app.utils.helpers import argument_list_type

from ..entities.models import Entity
from ..users.models import User, UserRoles
from ..users.resources import user_model
from .models import Role

api = ExtendedNameSpace("roles", description="Roles operations")

role_entity_permission_model = api.model(
    "RoleEntityPermission",
    {
        "name": fields.String(attribute="entity.name"),
        "canCreate": fields.Boolean(attribute="can_create"),
        "canEdit": fields.Boolean(attribute="can_edit"),
    },
)

roles_model = api.model(
    "Role",
    {
        "id": fields.Integer(),
        "name": fields.String(),
        "description": fields.String(),
        "users": fields.List(
            fields.Nested(user_model, skip_none=True),
            attribute=lambda role: User.query.join(
                UserRoles, UserRoles.user_id == User.id
            )
            .with_entities(User.id.label("id"), User.username.label("username"))
            .filter(UserRoles.role_id == role.id)
            .all(),
        ),
        "entities": fields.List(
            fields.Nested(role_entity_permission_model, skip_none=True),
            attribute="entity_permissions",
        ),
    },
)

role_parser_required = RequestParser()
role_parser_required.add_argument(
    "name", required=True, location="form", type=str
).add_argument("description", required=True, location="form", type=str)


role_parser = RequestParser()
role_parser.add_argument("name", location="form", type=str).add_argument(
    "description", location="form", type=str
)


class RolesResource(Resource):
    @jwt_required()
    @has_roles("admin")
    @api.marshal_list_with(roles_model, envelope="data")
    def get(self):

        return Role.query.all()

    @jwt_required()
    @has_roles("admin")
    @api.marshal_list_with(roles_model)
    @api.expect(role_parser_required)
    def post(self):
        args = role_parser.parse_args()
        new_role = Role(**args)
        new_role.save()

        return new_role


user_ids_parser = api.parser()
user_ids_parser.add_argument(
    "users",
    type=argument_list_type(int),
    required=True,
    location="json",
    help="A list of users' ids.",
)

users_ids_model = api.model("users_ids", {"users": fields.List(fields.Integer)})


@api.param("role_id", "role's id", type=int)
class RoleResource(Resource):
    @jwt_required()
    @has_roles("admin")
    @api.marshal_with(roles_model)
    def get(self, role_id: int):
        role_ = Role.get(role_id)
        if not role_:
            raise abort(404)
        return role_

    @jwt_required()
    @has_roles("admin")
    @api.marshal_with(roles_model)
    @api.expect(users_ids_model, validate=True)
    def post(self, role_id: int):
        role_ = Role.get(role_id)
        if not role_:
            raise abort(404)

        args = user_ids_parser.parse_args()
        if User.query.filter(User.id.in_(args.get("users"))).count() != len(
            args.get("users")
        ):
            raise InvalidUsage.custom_error("Can't add these users", 401)
        db.session.add_all(
            [UserRoles(user_id=user_id, role=role_) for user_id in args["users"]]
        )

        db.session.commit()

        return role_

    @jwt_required()
    @api.expect(role_parser)
    @has_roles("admin")
    @api.marshal_with(roles_model)
    def put(self, role_id: int):
        args = role_parser.parse_args()
        role: Role = Role.query.filter(Role.id == role_id).first_or_404()
        role.update(**args, ignore_none=True)

        return role


class RoleEntityPermissionsResource(Resource):

    parser = RequestParser()
    parser.add_argument(
        "entityId",
        dest="entity_id",
        type=int,
        location="json",
        required=True,
        help="id of entity to add to role's permission",
    )
    parser.add_argument("canCreate", dest="can_create", type=bool, location="json")
    parser.add_argument("canEdit", dest="can_edit", type=bool, location="json")

    @jwt_required()
    @has_roles("admin")
    @api.expect(parser)
    @api.marshal_with(roles_model)
    def post(self, role_id: int):
        role = Role.get(id=role_id)
        if not role:
            raise abort(404)
        args = self.parser.parse_args()
        entity = Entity.get(id=args.pop("entity_id"))
        if not entity:
            raise InvalidUsage.custom_error("invalid entity", 401)
        role.add_entity(entity, **args)

        return role

    @jwt_required()
    @has_roles("admin")
    @api.expect(parser)
    @api.marshal_with(roles_model)
    def put(self, role_id: int):
        role = Role.get(id=role_id)
        if not role:
            raise abort(404)
        args = self.parser.parse_args()
        entity_id = args.pop("entity_id")
        entity: List[Entity] = [
            ent for ent in role.entity_permissions if ent.entity_id == entity_id
        ]
        if len(entity) != 1:
            raise InvalidUsage.custom_error("invalid entity", 401)
        entity[0].update(ignore_none=True, **args)
        return role


api.add_resource(RolesResource, "/")
api.add_resource(RoleResource, "/<role_id>")
api.add_resource(RoleEntityPermissionsResource, "/<role_id>/entity")
