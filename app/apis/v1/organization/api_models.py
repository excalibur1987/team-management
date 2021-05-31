from flask_restx import fields

from app.apis.v1.users.resources import user_model
from app.utils.extended_objects import Nested

from .namespace import api

department_serializer = {"id": fields.Integer(), "name": fields.String()}
organization_department_model = api.model(
    "OrganizationDepartment", department_serializer
)


organization_serializer = {
    "id": fields.Integer(description="organization's id"),
    "name": fields.String(),
    "slug": fields.String(),
    "departments": Nested(organization_department_model, as_list=True),
    "description": fields.String(),
    "address": fields.String(
        attribute=lambda org: "\n".join([org.addr_line1, org.addr_line2])
    ),
    "country": fields.String(),
    "city": fields.String(),
    "email": fields.String(attribute="contact_email"),
    "phone": fields.String(attribute="contact_phone"),
    "contactPerson": Nested(
        user_model, attribute="contact_user", only=["username", "email", "phone"]
    ),
}

organization_model = api.model("Organization", organization_serializer)
