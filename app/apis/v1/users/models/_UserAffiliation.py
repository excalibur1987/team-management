from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer

from app.database import BaseModel
from app.exceptions import InvalidUsage

if TYPE_CHECKING:
    from app.apis.v1.organization.models import Organization, OrganizationDepartment

    from ._User import User


class UserAffiliation(BaseModel):
    VALID_POSITIONS = [
        "CEO",
        "Manager",
        "Assistant Manager",
        "Employee",
        "Trainee",
        "Other",
    ]

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="")

    org_id = Column(Integer, ForeignKey("organizations.id"), comment="")
    organization: "Organization" = relationship("Organization")

    department_id = Column(
        Integer, ForeignKey("organization_departments.id"), nullable=True, comment=""
    )
    department: "OrganizationDepartment" = relationship("OrganizationDepartment")

    position_id = Column(Integer, nullable=False, comment="")

    def get_position(self):

        return self.VALID_POSITIONS[self.position_id]

    def set_position(self, value: str):
        if value not in self.VALID_POSITIONS:
            raise InvalidUsage.custom_error("Invalid position", 401)
        self.position_id = [
            idx
            for idx, pos in enumerate(self.VALID_POSITIONS)
            if value.lower() == pos.lower()
        ][0]

    position = property(get_position, set_position)

    def __init__(
        self,
        user: "User",
        org: "Organization",
        position: str,
        org_dep: "OrganizationDepartment" = None,
    ) -> None:

        self.user_id = user.id
        self.org_id = org.id
        self.department_id = getattr(org_dep, "id", None)
        self.position = position
