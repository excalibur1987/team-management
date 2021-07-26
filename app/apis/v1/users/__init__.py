from .namespace import api
from .resources import (
    LoginResource,
    LogoutResource,
    UserInvitationResource,
    UserResource,
    UserSession,
    UserSessions,
    UserSignupResource,
    UsersResource,
)

api.add_resource(UsersResource, "/users")
api.add_resource(UserSignupResource, "/users/signup")
api.add_resource(LoginResource, "/user/login")
api.add_resource(LogoutResource, "/user/logout")
api.add_resource(UserResource, "/users/<int:user_id>", endpoint="user")
api.add_resource(UserResource, "/user")

api.add_resource(
    UserSessions,
    "/users/<int:user_id>/sessions",
    "/user/sessions",
    endpoint="sessions",
)
api.add_resource(
    UserSession,
    "/users/<int:user_id>/sessions/<slug>",
    "/user/sessions/<slug>",
    endpoint="single_session",
)
api.add_resource(
    UserInvitationResource,
    "/users/invitation/<slug>",
    endpoint="user_invitation",
)
