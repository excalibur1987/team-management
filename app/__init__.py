from typing import Type

from flask.app import Flask
from flask_jwt_extended import current_user

from app.blueprints import register_blueprints
from app.commands import register_commands
from app.extensions import register_extensions
from app.handlers import register_handlers
from app.settings import Config, DevConfig
from app.utils import chain


def create_app(config_object: Type[Config] = DevConfig) -> Flask:

    app = Flask(__name__, template_folder="templates")
    app.config.from_object(config_object)

    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)

    chained_function = chain(
        register_commands, register_blueprints, register_extensions, register_handlers
    )
    app = chained_function(app)

    return app
