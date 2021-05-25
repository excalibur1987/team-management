from datetime import datetime
from typing import TYPE_CHECKING

from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.expression import and_, cast
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BOOLEAN, DATE, INTEGER, String

from app.database import BaseModel, CancelableModel, DatedModel

if TYPE_CHECKING:
    from app.apis.v1.users.models import User  # NOQA


class Project(BaseModel, DatedModel, CancelableModel):
    """holds references to assets uploaded by users"""

    __tablename__ = "projects"

    title = Column(String, nullable=False, comment="Project's Title")
    description = Column(
        String, nullable=True, comment="Description for created project"
    )

    is_completed = Column(
        BOOLEAN,
        nullable=False,
        server_default=cast(True, BOOLEAN),
        comment="flags the project as complete",
    )

    start_date = Column(
        DATE,
        nullable=False,
        default=lambda: datetime.now(tz=current_app.config["TZ"]),
        comment="timestamp for project's start date",
    )
    time_frame = Column(
        INTEGER, nullable=False, comment="estimated time-frame for project in days"
    )

    @hybrid_property
    def active_users(self):
        from ._ProjectUser import ProjectUser

        return ProjectUser.query.filter(
            and_(ProjectUser.project_id == self.id, ProjectUser.is_active)
        ).all()
