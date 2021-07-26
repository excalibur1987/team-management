from flask import render_template
from flask.helpers import url_for
from flask_jwt_extended import jwt_required
from flask_restx import Resource
from flask_restx.reqparse import RequestParser
from sqlalchemy.sql.expression import and_

from app.apis.v1.users.api_models import user_invitation_model
from app.apis.v1.users.models import User, UserAffiliation, UserInvitation
from app.database import db
from app.exceptions import InvalidUsage
from app.extensions import mail
from app.settings import Config
from app.utils import current_user
from app.utils.extended_objects import IndexedAttribute
from app.utils.helpers import combine_parsers
from app.utils.parsers import DateParserType, offset_parser

from .api_models import organization_meta_model, organization_model
from .models import Organization, OrganizationDepartment
from .namespace import api


class OrganizationResource(Resource):
    @api.expect("organization", "organization's name", type=str)
    @api.marshal_with(organization_model)
    def get(self, organization: str):
        org = Organization.get(name=organization)
        return org


class InviteUserResource(Resource):
    invitaion_parser = RequestParser()
    invitaion_parser.add_argument(
        "name", type=str, required=True, location="form"
    ).add_argument(
        "email", type=lambda val: str(val).lower(), required=True, location="form"
    ).add_argument(
        "position",
        type=lambda val: str(val).upper(),
        required=True,
        choices=sorted([str(item) for item in Config.VALID_POSITIONS.items]),
        location="form",
    ).add_argument(
        "department",
        type=lambda val: str(val).upper(),
        choices=sorted([str(item) for item in Config.VALID_DEPARTMENTS.items]),
        location="form",
    ).add_argument(
        "customDepartment",
        dest="custom_department",
        type=lambda val: str(val).upper(),
        location="form",
    )

    @jwt_required()
    @api.expect(invitaion_parser)
    @api.marshal_with(user_invitation_model)
    def post(self, organization: str):
        organization: Organization = Organization.get(name=organization)

        if (
            current_user.affiliation.position != Config.VALID_POSITIONS.CEO
            and current_user.id != organization.contact_user_id
        ):
            raise InvalidUsage.user_not_authorized()
        args: dict = self.invitaion_parser.parse_args()

        if (
            User.query.filter(User.email == args.get("email")).count() > 0
            or UserInvitation.query.filter(
                UserInvitation.email == args.get("email")
            ).count()
            > 0
        ):
            raise InvalidUsage.custom_error("This email is already registered", 401)

        department: IndexedAttribute = IndexedAttribute(name=args.get("department"))
        department = (
            department
            if department != Config.VALID_DEPARTMENTS.OTHER
            else args.get("custom_department")
        )

        position: IndexedAttribute = Config.VALID_POSITIONS[args.get("position")]

        org_department = OrganizationDepartment.get(name=department.name)

        if position in [Config.VALID_POSITIONS.CEO, Config.VALID_POSITIONS.MANAGER]:
            registered_invitations = UserInvitation.query.filter(
                and_(
                    UserInvitation.position_id == position.id,
                    UserInvitation.department_id == getattr(org_department, "id"),
                    UserInvitation.cancelled_at.is_(None),
                )
            ).count()
            registered_users = (
                UserAffiliation.query.join(User, User.id == UserAffiliation.user_id)
                .filter(
                    and_(
                        UserAffiliation.position_id == position.id,
                        UserAffiliation.department_id == getattr(org_department, "id"),
                        User.active,
                    )
                )
                .count()
            )
            if registered_invitations > 0 or registered_users > 0:
                raise InvalidUsage.custom_error(
                    "There's already a user with that posisition", 401
                )

        if org_department is None:
            org_department = OrganizationDepartment(
                department=department, org=organization
            )
        org_department.save()
        db.session.flush()

        invitation: UserInvitation = UserInvitation(
            org=organization,
            position=position,
            email=args.get("email"),
            name=args.get("name"),
            org_dep=org_department,
        )

        invitation.save()

        db.session.commit()

        message_html = render_template(
            "user_invitation.html",
            organization=organization,
            url=url_for("v1.user_invitation", slug=invitation.slug, absolute=True),
            greeting=invitation.name,
        )
        mail.send_message(
            subject=f"Invitation from {current_user.name} to join {organization.name}",
            recipients=[invitation.email],
            html=message_html,
        )

        return invitation

    query_parser = RequestParser()
    query_parser.add_argument("active", type=bool).add_argument(
        "createdAt", dest="created_at", type=DateParserType(True)
    )

    @jwt_required()
    @api.expect(
        combine_parsers(
            offset_parser,
            query_parser,
        )
    )
    @api.serialize_multi(user_invitation_model, UserInvitation)
    def get(self, organization: str):
        organization: Organization = Organization.get(name=organization)

        if (
            current_user.affiliation.position != Config.VALID_POSITIONS.CEO
            and current_user.id != organization.contact_user_id
        ):
            raise InvalidUsage.user_not_authorized()

        offset_args = offset_parser.parse_args()
        query_args = self.query_parser.parse_args()

        result = (
            UserInvitation.query.filter(
                and_(
                    *[
                        (getattr(UserInvitation, k) == v)
                        for k, v in query_args.items()
                        if v is not None
                    ]
                )
            )
            .order_by(UserInvitation.id.asc())
            .offset(offset_args.get("offset", 0))
            .limit(offset_args.get("limit", 10))
            .all()
        )

        return result


class OrganizationMetaResource(Resource):
    @api.marshal_with(organization_meta_model)
    def get(self):

        return {
            "department": Config.VALID_DEPARTMENTS.items,
            "positions": Config.VALID_POSITIONS.items,
        }
