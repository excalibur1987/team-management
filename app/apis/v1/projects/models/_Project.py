from datetime import date, datetime
from typing import TYPE_CHECKING, List
from uuid import uuid4

from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import and_, cast
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BOOLEAN, DATE, INTEGER, Integer, String
from werkzeug import datastructures

from app.database import BaseModel, CancelableModel, DatedModel
from app.utils import FileHandler

if TYPE_CHECKING:
    from app.apis.v1.organization.models import Organization

    from ._ProjectAsset import ProjectAsset  # NOQA


class Project(BaseModel, DatedModel, CancelableModel):
    """holds references to assets uploaded by users"""

    __tablename__ = "projects"

    title = Column(String, nullable=False, comment="Project's Title")
    description = Column(
        String, nullable=True, comment="Description for created project"
    )

    slug = Column(String, unique=True, nullable=False, comment="unique project's slug")

    org_id = Column(Integer, ForeignKey("organizations.id"), comment="")
    organization: "Organization" = relationship("Organization")

    is_completed = Column(
        BOOLEAN,
        nullable=False,
        server_default=cast(True, BOOLEAN),
        comment="flags the project as complete",
    )

    is_public = Column(
        BOOLEAN,
        nullable=False,
        server_default=cast(True, BOOLEAN),
        comment="flags the project as public",
    )

    start_date = Column(
        DATE,
        nullable=False,
        default=lambda: datetime.now(tz=current_app.config["TZ"]).date(),
        comment="project's start date",
    )
    time_frame = Column(
        INTEGER, nullable=False, comment="estimated time-frame for project in days"
    )

    logo = Column(String, nullable=True, comment="url to project's logo")

    assets: List["ProjectAsset"] = relationship("ProjectAsset", uselist=True)

    def __init__(
        self,
        title: str,
        description: str,
        start_date: date,
        end_date: date = None,
        time_frame: int = None,
        public: bool = True,
        logo: datastructures.FileStorage = None,
    ) -> None:
        self.title = title
        self.description = description
        self.start_date = start_date
        self.is_completed = False
        self.time_frame = time_frame or (end_date - start_date).days
        if logo:
            self.logo_handler = FileHandler(data=logo.stream, title=logo.filename)
            self.logo = self.logo_handler.url
        self.is_public = public
        self.slug = uuid4()

    def save(self):
        if getattr(self, "logo_handler", None) is not None:
            self.logo_handler.save()
        super().save(persist=True)

    def delete(self):
        super().delete(persist=True)
        FileHandler(url=self.logo).delete()

    @hybrid_property
    def active_users(self):
        from app.apis.v1.users.models import User

        from ._ProjectUser import ProjectUser

        return (
            ProjectUser.query.join(User, User.id == ProjectUser.user_id)
            .with_entities(
                User.id.label("id"),
                User.name.label("name"),
                ProjectUser.is_active.label("active"),
            )
            .filter(
                and_(
                    ProjectUser.project_id == self.id,
                    ProjectUser.cancelled_at.is_not(None),
                )
            )
            .all()
        )
