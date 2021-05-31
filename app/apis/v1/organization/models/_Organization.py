from typing import TYPE_CHECKING, List
from uuid import uuid4

from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String

from app.database import BaseModel, DatedModel

if TYPE_CHECKING:
    from app.apis.v1.users.models import User

    from ._OrganizationDepartment import OrganizationDepartment


class Organization(BaseModel, DatedModel):

    __tablename__ = "organizations"

    name = Column(
        String, unique=True, nullable=False, comment="Unique name of Organization"
    )
    description = Column(
        String, nullable=True, comment="Short description of organization"
    )

    addr_line1 = Column(String, nullable=False, comment="Address line 1")
    addr_line2 = Column(String, nullable=True, comment="Address line 1")

    country = Column(String, nullable=False, comment="Country's ISO code")
    city = Column(String, nullable=False, comment="City's name")

    contact_email = Column(String, nullable=False, comment="")
    contact_phone = Column(String, nullable=False, comment="")

    contact_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contact_user: "User" = relationship(
        "User", foreign_keys=[contact_user_id], uselist=False
    )

    slug = Column(
        String, unique=True, nullable=False, comment="identifier slug for organization"
    )

    departments: List["OrganizationDepartment"] = relationship(
        "OrganizationDepartment", uselist=True
    )

    def __init__(
        self,
        name: str = None,
        description: str = None,
        addr_line1: str = None,
        addr_line2: str = None,
        country: str = None,
        city: str = None,
        email: str = None,
        phone: str = None,
        contact_user_id: int = None,
        **kwargs
    ) -> None:
        super().__init__()
        self.name = name
        self.description = description
        self.addr_line1 = addr_line1
        self.addr_line2 = addr_line2
        self.country = country
        self.city = city
        self.contact_email = email
        self.contact_phone = phone
        self.contact_user_id = contact_user_id
        self.slug = uuid4()
