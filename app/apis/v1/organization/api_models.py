from flask_restx import fields

from app.apis.v1.users.api_models import user_model
from app.utils.extended_objects import Nested

from .namespace import api

organization_meta_entity_model = api.model(
    "OrganizationMetaEntityModel", {"id": fields.Integer(), "name": fields.String()}
)
organization_meta_model = api.model(
    "OrganizationMetaModel",
    {
        "department": fields.Nested(organization_meta_entity_model),
        "positions": fields.Nested(organization_meta_entity_model),
    },
)

organization_serializer = {
    "id": fields.Integer(description="organization's id"),
    "name": fields.String(),
    "slug": fields.String(),
    "departments": Nested(organization_meta_model, as_list=True),
    "description": fields.String(),
    "address": fields.String(
        attribute=lambda org: "\n".join([org.addr_line1, org.addr_line2])
    ),
    "country": fields.String(),
    "city": fields.String(),
    "email": fields.String(attribute="contact_email"),
    "phone": fields.String(attribute="contact_phone"),
    "contactPerson": Nested(
        user_model,
        attribute="contact_user",
        only=["username", "email", "phone"],
        skip_none=True,
    ),
}

organization_model = api.model("Organization", organization_serializer)
