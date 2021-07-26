from flask_restx import fields

from app.apis.v1.users.api_models import user_model
from app.utils.extended_objects import Nested

from .namespace import api

entity_serializer = {"id": fields.Integer(), "name": fields.String()}

organization_meta_entity_model = api.model(
    "OrganizationMetaEntityModel", entity_serializer
)

affiliation_model = api.model(
    "UserAffiliation",
    {
        "position": fields.String(),
        "photo": fields.String(attribute="user._photo"),
        "name": fields.String(attribute="user.name"),
        "id": fields.Integer(attribute="user_id"),
    },
)

organization_department_model = api.model(
    "OrganizationDepartment",
    {
        **entity_serializer,
        "users": Nested(affiliation_model, as_list=True, attribute="affiliation"),
    },
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
    "ceo": Nested(
        affiliation_model,
    ),
    "departments": Nested(organization_department_model, as_list=True),
    "description": fields.String(),
    "address": fields.String(
        attribute=lambda org: org.addr_line1
        + f"{' ' + org.addr_line2 if org.addr_line2 else ''}"
    ),
    "country": fields.String(),
    "city": fields.String(),
    "email": fields.String(attribute="contact_email"),
    "phone": fields.String(attribute="contact_phone"),
    "contactPerson": Nested(
        user_model,
        attribute="contact_user",
        only=["id", "name", "photo"],
        skip_none=True,
    ),
}

organization_model = api.model("Organization", organization_serializer)
