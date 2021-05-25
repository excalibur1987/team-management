from typing import TYPE_CHECKING

from sqlalchemy import cast
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BOOLEAN, INTEGER

from app.database import BaseModel

if TYPE_CHECKING:
    from app.apis.v1.users.models import User


class AssetPermission(BaseModel):
    """permissions on assets granted to users"""

    __tablename__ = "asset_permissions"

    asset_id = Column(
        INTEGER, ForeignKey("asset_storage.id"), comment="asset reference id"
    )

    user_id = Column(INTEGER, ForeignKey("users.id"), comment="user's id")
    user = relationship("User")

    can_update = Column(
        BOOLEAN,
        nullable=False,
        server_default=cast(False, BOOLEAN),
        comment="if the user can update the asset",
    )
    can_delete = Column(
        BOOLEAN,
        nullable=False,
        server_default=cast(False, BOOLEAN),
        comment="if the user can delete the asset",
    )

    def __init__(
        self, user: "User", delete: bool = False, update: bool = False
    ) -> None:
        self.asset_id = user.id
        self.can_delete = delete
        self.can_update = update
