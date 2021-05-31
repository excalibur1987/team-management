from .namespace import api
from .resources import (
    LoginResource,
    LogoutResource,
    UserResource,
    UserSession,
    UserSessions,
    UsersResource,
)

api.add_resource(UsersResource, "/")
api.add_resource(LoginResource, "/login")
api.add_resource(LogoutResource, "/logout")
api.add_resource(UserResource, "/<int:user_id>", endpoint="user")
api.add_resource(
    UserSessions,
    "/<int:user_id>/sessions",
    endpoint="sessions",
)
api.add_resource(
    UserSession,
    "/<int:user_id>/sessions/<slug>",
    endpoint="single_session",
)
