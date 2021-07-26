from typing import TYPE_CHECKING

from flask import current_app
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer

from app.database import BaseModel
from app.utils.extended_objects import IndexedAttribute

if TYPE_CHECKING:
    from app.apis.v1.organization.models import Organization, OrganizationDepartment

    from ._User import User


class UserAffiliation(BaseModel):

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="")
    user: "User" = relationship("User")

    org_id = Column(Integer, ForeignKey("organizations.id"), comment="")
    organization: "Organization" = relationship("Organization")

    department_id = Column(
        Integer, ForeignKey("organization_departments.id"), nullable=True, comment=""
    )
    department: "OrganizationDepartment" = relationship("OrganizationDepartment")

    position_id = Column(Integer, nullable=False, comment="")

    def get_position(self):

        return current_app.config["VALID_POSITIONS"][self.position_id]

    def set_position(self, value: IndexedAttribute):
        self.position_id = value.id

    position = property(get_position, set_position)

    def __init__(
        self,
        user: "User",
        org: "Organization",
        position: IndexedAttribute,
        org_dep: "OrganizationDepartment" = None,
    ) -> None:

        self.user_id = user.id
        self.org_id = org.id
        self.department_id = getattr(org_dep, "id", None)
        self.position = position
