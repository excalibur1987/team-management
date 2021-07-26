from .namespace import api
from .resources import (
    InviteUserResource,
    OrganizationMetaResource,
    OrganizationResource,
)

api.add_resource(OrganizationResource, "/<organization>")
api.add_resource(OrganizationMetaResource, "/meta-info")
api.add_resource(InviteUserResource, "/<organization>/invite")
