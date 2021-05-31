from collections import namedtuple

from flask.globals import current_app
from flask_restx import Resource

from .api_models import organization_department_model, organization_model
from .models import Organization
from .namespace import api


class OrganizationResource(Resource):
    @api.expect("org_name", "organization's name", type=str)
    @api.marshal_with(organization_model)
    def get(self, org_name: str):

        return Organization.get(name=org_name)


class DepartmentsResource(Resource):
    @api.marshal_with(organization_department_model)
    def get(self):
        Named_Department = namedtuple("Department", ["id", "name"])
        return [
            Named_Department(id=idx, name=dep)
            for idx, dep in enumerate(current_app.config["VALID_DEPARTMENTS"])
        ]
