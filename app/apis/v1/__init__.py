from flask import Blueprint
from flask_restx import Api

from .entities import api as entity_api
from .roles import api as roles_api
from .users import api as user_api

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

api_v1.add_namespace(roles_api)
api_v1.add_namespace(user_api)
api_v1.add_namespace(entity_api)
