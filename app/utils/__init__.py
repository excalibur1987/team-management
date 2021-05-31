from typing import TYPE_CHECKING

from flask import g
from flask_jwt_extended import current_user
from flask_principal import Identity

from .decorators import has_roles
from .extended_objects import ExtendedNameSpace, Nested
from .file_handler import FileHandler
from .helpers import chain, combine_parsers
from .url_w_args import UrlWArgs

if TYPE_CHECKING:
    from app.apis.v1.users.models import Session, User  # NOQA


class GlobalObject(object):
    identity: Identity
    session: "Session"


g: GlobalObject

current_user: "User"
