from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BOOLEAN, INTEGER

from app.apis.v1.entities.models import Entity
from app.database import BaseModel

if TYPE_CHECKING:
    from ._User import User


class UserEntityPermission(BaseModel):

    __tablename__ = "user_entity_permissions"

    entity_id = Column(
        INTEGER,
        ForeignKey("entities.id"),
        nullable=False,
        comment="entity's table foreign key",
    )
    entity = relationship("Entity")
    user_id = Column(
        INTEGER,
        ForeignKey("users.id"),
        nullable=False,
        comment="user's table foreign key",
    )
    can_create = Column(
        BOOLEAN,
        nullable=False,
        server_default=cast(False, BOOLEAN),
        comment="can create flag",
    )
    can_edit = Column(
        BOOLEAN,
        nullable=False,
        server_default=cast(False, BOOLEAN),
        comment="can edit flag",
    )

    def __init__(
        self,
        entity: "Entity",
        user: "User",
        can_create: bool = False,
        can_edit: bool = False,
    ) -> None:
        self.entity_id = entity.id
        self.user_id = user.id
        self.can_create = can_create
        self.can_edit = can_edit
