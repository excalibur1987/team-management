from .namespace import api
from .resources import DepartmentsResource, OrganizationResource

api.add_resource(OrganizationResource, "/<org_name>")
api.add_resource(DepartmentsResource, "/departments")
