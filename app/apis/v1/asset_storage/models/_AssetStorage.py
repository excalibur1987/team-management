from typing import TYPE_CHECKING

from app.database import BaseModel, DatedModel
from app.utils import FileHandler
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.util.langhelpers import hybridproperty
from werkzeug import datastructures

if TYPE_CHECKING:
    from app.apis.v1.users.models import User  # NOQA

    from ._AssetPermission import AssetPermission  # NOQA


class AssetStorage(BaseModel, DatedModel):
    """holds references to assets uploaded by users"""

    __tablename__ = "asset_storage"

    ref_id = Column(String, nullable=False, unique=True, comment="unique id for file")
    title = Column(String, nullable=False, comment="file title with extension")
    url = Column(String, nullable=False, comment="file url")

    user_permissions = relationship("AssetPermission", uselist=True)

    def __init__(self, file: datastructures.FileStorage, **kwargs) -> None:
        super(DatedModel, self).__init__(**kwargs)
        handler = FileHandler(data=file.stream, name=file.filename)
        handler.save()
        self.url = handler.url
        self.title = file.filename
        self.ref_id = handler.handler.file_object.key

    def delete(self, persist=False):
        handler = FileHandler(url=self.url)
        handler.delete()
        super().delete(persist=persist)

    @hybridproperty
    def handler(self):
        return FileHandler(url=self.url)
