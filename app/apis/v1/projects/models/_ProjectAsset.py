from typing import TYPE_CHECKING, List

from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import INTEGER

from app.database import BaseModel, DatedModel

if TYPE_CHECKING:
    from app.apis.v1.asset_storage.models import AssetStorage  # NOQA

    from ._Project import Project  # NOQA


class ProjectAsset(BaseModel, DatedModel):
    """references for assets available to projects"""

    project_id = Column(INTEGER, ForeignKey("projects.id"))

    asset_id = Column(INTEGER, ForeignKey("asset_storage.id"))
    asset: List["AssetStorage"] = relationship("AssetStorage")

    def __init__(self, project: "Project", asset: "AssetStorage") -> None:
        self.project_id = project.id
        self.asset_id = asset.id
