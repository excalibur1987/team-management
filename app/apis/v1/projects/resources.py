from datetime import timedelta
from typing import List

from flask_jwt_extended import jwt_required
from flask_restx import Resource, fields
from sqlalchemy import and_
from sqlalchemy.sql.expression import or_, select

from app.utils import current_user
from app.utils.decorators import has_permission
from app.utils.extended_objects import ExtendedNameSpace

from ..users import api as users_api
from .models import Project, ProjectUser
from .parsers import project_parser, query_parser

api = ExtendedNameSpace("projects", description="Projects operations")


project_asset_model = api.model(
    "ProjectAsset",
    {
        "id": fields.Integer(description="Asset's id"),
        "title": fields.String(attribute="asset.title"),
        "url": fields.String(attribute="asset.url"),
    },
)

project_model = api.model(
    "Project",
    {
        "id": fields.Integer(description="Project's id"),
        "title": fields.String(description="Project's Title"),
        "description": fields.String(description="Short description"),
        "completed": fields.Boolean(
            attribute="is_completed", description="flags project as complete"
        ),
        "public": fields.Boolean(
            attribute="is_public", description="flags project as public"
        ),
        "logo": fields.String(),
        "startDate": fields.Date(
            attribute="start_date", description="project's start date"
        ),
        "endDate": fields.Date(
            attribute=lambda proj: proj.start_date + timedelta(days=proj.time_frame),
            description="",
        ),
        "users": fields.List(
            fields.Nested(users_api.models["User"], attribute="active_users"),
            read_only=True,
        ),
        "assets": fields.List(fields.Nested(project_asset_model), read_only=True),
    },
)


class ProjectsResource(Resource):
    @jwt_required()
    @api.expect(query_parser)
    @api.marshal_list_with(project_model)
    def get(self):
        query_args: dict = query_parser.parse_args()
        offset_args = {
            "offset": query_args.pop("offset", 0),
            "limit": query_args.pop("limit", 0),
        }
        public: bool = query_args.pop("is_public", True)
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
                                public,
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


api.add_resource(ProjectsResource, "/")
