from flask import Blueprint
from flask_restx import Api

api_v1_bp = Blueprint("v1", __name__, url_prefix="/v1")
api_v1 = Api(
    api_v1_bp,
    version="1",
    title="Backend Api",
    authorizations={
        "apikey": {"type": "apiKey", "in": "header", "name": "X-CSRF-TOKEN"}
    },
    security="apikey",
)


def register_namespaces(api_: Api) -> Api:

    from .users import api as user_api

    api_v1.add_namespace(user_api)

    from .roles import api as roles_api

    api_v1.add_namespace(roles_api)

    from .entities import api as entity_api

    api_v1.add_namespace(entity_api)

    from .projects import api as project_api

    api_v1.add_namespace(project_api)

    from .organization import api as organization_api

    api_v1.add_namespace(organization_api)

    return api_


api_v1 = register_namespaces(api_v1)
