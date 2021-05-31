from datetime import timedelta

from flask_restx import fields

from app.apis.v1.users.api_models import user_model
from app.utils.extended_objects import Nested

from .namespace import api

project_asset_serializer = {
    "id": fields.Integer(description="Asset's id"),
    "title": fields.String(attribute="asset.title"),
    "url": fields.String(attribute="asset.url"),
}
project_asset_model = api.model(
    "ProjectAsset",
    project_asset_serializer,
)


project_serializer = {
    "id": fields.Integer(description="Project's id"),
    "title": fields.String(description="Project's Title"),
    "description": fields.String(description="Short description"),
    "slug": fields.String(description="project's identifier slug"),
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
    "users": Nested(
        user_model,
        only=[
            "id",
            "name",
            "active",
        ],
        attribute="active_users",
        as_list=True,
        read_only=True,
    ),
    "assets": fields.Nested(project_asset_model, read_only=True, as_list=True),
}
project_model = api.model(
    "Project",
    project_serializer,
)
