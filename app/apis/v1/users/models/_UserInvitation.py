import random
import string
from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String

from app.database import BaseModel, CancelableModel, DatedModel
from app.exceptions import InvalidUsage
from app.settings import Config

if TYPE_CHECKING:
    from app.apis.v1.organization.models import Organization, OrganizationDepartment

    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property  # NOQA


class UserInvitation(BaseModel, DatedModel, CancelableModel):
    """Holds users' data"""

    __tablename__ = "users_invitations"
    name = Column(String, nullable=False, comment="user's name")
    email = Column(
        String, nullable=True, unique=True, comment="User's personal unique email"
    )
    org_id = Column(Integer, ForeignKey("organizations.id"), comment="")
    organization: "Organization" = relationship("Organization")

    department_id = Column(
        Integer, ForeignKey("organization_departments.id"), nullable=True, comment=""
    )
    department: "OrganizationDepartment" = relationship("OrganizationDepartment")

    position_id = Column(Integer, nullable=False, comment="")

    slug = Column(String, nullable=False, comment="")

    def get_position(self):

        return Config.VALID_POSITIONS[self.position_id]

    def set_position(self, value: str):
        if value not in Config.VALID_POSITIONS.items():
            raise InvalidUsage.custom_error("Invalid position", 401)
        self.position_id = Config.VALID_POSITIONS[value].id

    position = property(get_position, set_position)

    def __init__(
        self,
        name: str,
        org: "Organization",
        position: str,
        email: str,
        org_dep: "OrganizationDepartment" = None,
    ) -> None:
        self.name = name
        self.email = email.lower()
        self.org_id = org.id
        self.department_id = getattr(org_dep, "id", None)
        self.position = position
        self.slug = random.choices(
            string.ascii_uppercase + string.digits + string.ascii_lowercase, k=100
        )
