from typing import TYPE_CHECKING

from app.database import BaseModel, db
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String

if TYPE_CHECKING:
    from ...entities.models import Entity
    from ._RoleEntityPermission import RoleEntityPermission  # NOQA


class Role(BaseModel):
    """contains basic roles for the aplication"""

    __tablename__ = "roles"
    name = Column(String, nullable=False, comment="role name")
    description = Column(
        String,
        nullable=False,
        server_default="",
        comment="short discription of the role",
    )

    entity_permissions = relationship("RoleEntityPermission",)

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    def add_entity(self, entity: "Entity", create: bool = False, edit: bool = False):
        from ._RoleEntityPermission import RoleEntityPermission  # NOQA

        permission = RoleEntityPermission(entity=entity, role=self, create=create, edit=edit)
        db.session.add(permission)
        db.session.commit()
