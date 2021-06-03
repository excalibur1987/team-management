from .namespace import api
from .resources import (
    OrganizationMetaResource,
    OrganizationResource,
    UserInvitationResource,
)

api.add_resource(OrganizationResource, "/<organization>")
api.add_resource(OrganizationMetaResource, "/meta-info")
api.add_resource(UserInvitationResource, "/<organization>/invite")
