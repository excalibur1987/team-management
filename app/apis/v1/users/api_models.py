from flask_jwt_extended.utils import get_jwt
from flask_restx import fields

from app.utils import UrlWArgs

from .namespace import api

affiliation_serializer = {
    "name": fields.String(attribute=".department.name"),
    "position": fields.String(),
}

affiliation_model = api.model("AffiliationModel", affiliation_serializer)


user_serializer = {
    "id": fields.Integer(description="User unique identifier"),
    "username": fields.String(attribute="username"),
    "name": fields.String(description="User's fullname"),
    "active": fields.Boolean,
    "email": fields.String(description="User's email"),
    "photo": fields.String(description="Url for user's avatar", attribute="photo.url"),
    "phone": fields.String,
    "roles": fields.List(
        fields.String(attribute="name"), description="A list of user roles"
    ),
    "token": fields.String(default=None),
    "organization": fields.String(attribute="affiliation.organization.name"),
    "department": fields.Nested(
        affiliation_model,
        attribute="affiliation",
    ),
}

user_model = api.model(
    "User",
    user_serializer,
)

session_serializer = {
    "id": fields.Integer(description="Session's unique id"),
    "ipAddress": fields.String(
        attribute="ip_address", description="Logged-in Machine's IP"
    ),
    "platform": fields.String(
        attribute="platform", default="N/A", description="Logged-in os platform"
    ),
    "browser": fields.String(
        attribute="browser", default="N/A", description="Logged-in browser"
    ),
    "createdAt": fields.DateTime(
        attribute="created_at", description="Session creation date"
    ),
    "active": fields.Boolean(
        attribute=lambda session_: session_.token == get_jwt().get("jti", None),
        description="If this is the current active sessions",
    ),
    "url": UrlWArgs(
        endpoint=".single_session",
        user_id=".user_id",
        slug=".slug",
        description="Session endpoint",
    ),
}

session_model = api.model("Session", session_serializer)
