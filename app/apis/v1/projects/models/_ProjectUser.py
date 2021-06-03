from typing import TYPE_CHECKING, List, Literal

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BOOLEAN, INTEGER, SMALLINT
from typing_extensions import TypeAlias

from app.database import BaseModel, CancelableModel, DatedModel

if TYPE_CHECKING:
    from app.apis.v1.users.models import User

    from ._Project import Project

RoleType: TypeAlias = Literal["admin", "editor", "viewer"]


class ProjectUser(BaseModel, DatedModel, CancelableModel):
    """holds references to users assigned to a project"""

    __tablename__ = "project_users"

    PROJECT_ROLES: List[RoleType] = ["admin", "editor", "viewer"]

    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

    project_id = Column(INTEGER, ForeignKey("projects.id"))

    user_id = Column(INTEGER, ForeignKey("users.id"))
    user = relationship("User", foreign_keys=[user_id], uselist=False)

    is_active = Column(
        BOOLEAN,
        nullable=False,
        server_default=cast(True, BOOLEAN),
        comment="flags the validity of user in the project",
    )

    role_id = Column(SMALLINT, nullable=False, comment="user's role in this project")

    def __init__(self, project: "Project", user: "User", role: RoleType) -> None:
        assert role in ProjectUser.PROJECT_ROLES
        self.project_id = project.id
        self.user_id = user.id
        self.role_id = ProjectUser.PROJECT_ROLES.id(role)

    @hybrid_property
    def role(self) -> RoleType:
        return ProjectUser.PROJECT_ROLES[self.role_id]
