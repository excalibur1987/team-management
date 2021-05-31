import json
from typing import List

from flask_jwt_extended import jwt_required
from flask_principal import Permission
from flask_restx import Resource, fields
from flask_restx.reqparse import RequestParser
from sqlalchemy import and_
from sqlalchemy.sql.expression import cast, or_, select
from sqlalchemy.sql.sqltypes import BOOLEAN

from app.exceptions import InvalidUsage
from app.utils import current_user, g
from app.utils.custom_principal_needs import ProjectNeed
from app.utils.decorators import has_permission
from app.utils.helpers import argument_list_type, combine_parsers
from app.utils.parsers import offset_parser

from ..users.api_models import user_model
from ..users.models import User
from .api_models import project_model
from .models import Project, ProjectUser
from .namespace import api
from .parsers import project_parser, query_parser


class ProjectsResource(Resource):
    @jwt_required()
    @api.expect(combine_parsers(query_parser, offset_parser))
    @api.serialize_multi(project_model, Project)
    def get(self):
        query_args: dict = query_parser.parse_args()
        offset_args: dict = offset_parser.parse_args()
        public: bool = json.loads(query_args.pop("is_public", "true"))
        projects: List[Project] = (
            Project.query.filter(
                and_(
                    *(
                        [
                            (getattr(Project, k) == v)
                            for k, v in query_args.items()
                            if v is not None
                        ]
                        + [
                            or_(
                                Project.id.in_(
                                    select(ProjectUser.project_id).where(
                                        current_user.id == ProjectUser.user_id
                                    )
                                ),
                                cast(public, BOOLEAN),
                            )
                        ]
                    )
                )
            )
            .offset(offset_args.get("offset", 0))
            .limit(offset_args.get("limit", 10))
            .all()
        )

        return projects

    @jwt_required()
    @has_permission("project")
    @api.expect(
        project_parser,
    )
    @api.marshal_with(project_model)
    def post(self):
        args = project_parser.parse_args()
        project = Project(**args)
        project.save()
        return project


@api.expect("project_slug")
class ProjectResource(Resource):
    @jwt_required()
    @api.marshal_with(project_model)
    def get(self, project_slug: str):
        """Get project's info"""

        return Project.query.filter(
            and_(
                Project.slug == project_slug,
                or_(
                    Project.id.in_(
                        select(ProjectUser.project_id).where(
                            current_user.id == ProjectUser.user_id
                        )
                    ),
                    Project.is_public,
                ),
            )
        ).first()

    @jwt_required()
    @api.marshal_with(project_model)
    def put(self, project_slug: str):
        """Update project's info"""
        if not g.identity.can(Permission(ProjectNeed(project_slug))):
            raise InvalidUsage.user_not_authorized()
        return Project.get(slug=project_slug)


class ProjectInviteResource(Resource):
    parser = RequestParser()
    parser.add_argument(
        "users", type=argument_list_type(int), location="json", required=True
    )

    @api.expect(parser)
    @api.response(
        200,
        "List of users who were sent an invitaion",
        api.model("ProjectUsers", {"users": fields.Nested(user_model, as_list=True)}),
    )
    @api.response(401, "Invalid users' data supplied")
    def post(self, project_slug: str):

        users_ids: List[int] = self.parser.parse_args()

        users: List[User] = User.query.filter(User.id.in_(users_ids)).all()

        if len(users) != len(users_ids):
            raise InvalidUsage.custom_error("Users data supplied are invalid", 401)

        return [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
            }
            for user in users
        ]
