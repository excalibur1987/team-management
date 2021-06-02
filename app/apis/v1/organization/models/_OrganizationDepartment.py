from typing import TYPE_CHECKING, List

from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String

from app.database import BaseModel

if TYPE_CHECKING:
    from app.apis.v1.users.models import User  # NOQA

    from ._Organization import Organization


class OrganizationDepartment(BaseModel):

    __tablename__ = "organization_departments"

    org_id = Column(Integer, ForeignKey("organizations.id"), comment="")
    name = Column(String, nullable=False, comment="department's name")

    def __init__(
        self,
        id: int = None,
        name: str = None,
        org: "Organization" = None,
    ) -> None:
        self.org_id = org.id
        self.name = (
            current_app.config["VALID_DEPARTMENTS"][id]
            if id is not None
            and len(current_app.config["VALID_DEPARTMENTS"].items) > id
            else name
        )

    @hybrid_property
    def users(self) -> List["User"]:
        from app.apis.v1.users.models import User, UserAffiliation

        return User.query.filter(
            User.id.in_(
                UserAffiliation.query.with_entities(UserAffiliation.user_id)
                .filter(UserAffiliation.department_id == self.id)
                .subquery()
            )
        ).all()
