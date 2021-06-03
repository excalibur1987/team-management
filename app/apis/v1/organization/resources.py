from flask.globals import current_app
from flask_jwt_extended import jwt_required
from flask_restx import Resource
from flask_restx.reqparse import RequestParser

from app.exceptions import InvalidUsage
from app.settings import Config
from app.utils import current_user
from app.utils.custom_principal_needs import OrganizationNeed
from app.utils.decorators import has_endpoint_permission

from .api_models import organization_meta_model, organization_model
from .models import Organization
from .namespace import api


class OrganizationResource(Resource):
    @api.expect("organization", "organization's name", type=str)
    @api.marshal_with(organization_model)
    def get(self, organization: str):
        org = Organization.get(name=organization)
        return org


class UserInvitationResource(Resource):
    invitaion_parser = RequestParser()
    invitaion_parser.add_argument("email", type=str, required=True).add_argument(
        "position",
        type=str,
        required=True,
        choices=sorted([str(item) for item in Config.VALID_POSITIONS.items]),
    ).add_argument(
        "department",
        type=str,
        choices=sorted([str(item) for item in Config.VALID_DEPARTMENTS.items]),
    )

    @jwt_required()
    @api.expect(invitaion_parser)
    @has_endpoint_permission("organization", OrganizationNeed)
    def post(self, organization: str):
        organization: Organization = Organization.get(name=organization)

        if (
            current_user.affiliation.position
            != current_app.config["VALID_POSITIONS"].CEO
            and current_user.id != organization.contact_user_id
        ):
            raise InvalidUsage.user_not_authorized()

        return


class OrganizationMetaResource(Resource):
    @api.marshal_with(organization_meta_model)
    def get(self):

        return {
            "department": Config.VALID_DEPARTMENTS.items,
            "positions": Config.VALID_POSITIONS.items,
        }
