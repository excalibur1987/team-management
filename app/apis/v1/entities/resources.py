from flask_jwt_extended.view_decorators import jwt_required
from flask_restx import Resource, fields
from flask_restx.reqparse import RequestParser

from app.exceptions import InvalidUsage
from app.utils.decorators import has_roles
from app.utils.extended_objects import ExtendedNameSpace
from app.utils.parsers import offset_parser

from .models import Entity

api = ExtendedNameSpace("entities", description="Entities resources")

entity_model = api.model(
    "Entity",
    {
        "id": fields.Integer(description="Entity's id"),
        "name": fields.String(description="Entity's unique name"),
        "description": fields.String(description="Short description"),
    },
)

entity_parser = RequestParser()
entity_parser.add_argument("name", required=True, location="form", type=str)
entity_parser.add_argument("description", required=True, location="form", type=str)


class EntitiesResource(Resource):
    @jwt_required()
    @api.expect(offset_parser)
    @has_roles("admin")
    @api.serialize_multi(entity_model, Entity, description="List of Entities")
    def get(self):
        """Gets a list of user's active sessions"""
        args = offset_parser.parse_args()

        entities = (
            Entity.query.order_by(Entity.id.asc())
            .offset(args.get("offset", 0))
            .limit(args.get("limit", 10))
            .all()
        )
        return entities

    @jwt_required()
    @api.expect(entity_parser)
    @has_roles("admin")
    @api.marshal_with(entity_model)
    def post(self):
        args = entity_parser.parse_args()

        if Entity.query.filter_by(name=args.get("name")).count() > 0:
            raise InvalidUsage.custom_error("There's an entity with the same name", 401)

        entity = Entity(**args)
        entity.save()

        return entity


api.add_resource(EntitiesResource, "/")
