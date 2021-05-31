from .namespace import api
from .resources import ProjectInviteResource, ProjectResource, ProjectsResource

api.add_resource(ProjectsResource, "/projects/")
api.add_resource(ProjectResource, "/projects/<project_slug>")
api.add_resource(ProjectInviteResource, "/projects/<project_slug>/invite")
