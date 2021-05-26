from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String

from app.database import BaseModel


class Entity(BaseModel):

    __tablename__ = "entities"

    name = Column(String, nullable=False, unique=True, comment="entity name")
    description = Column(
        String,
        nullable=False,
        server_default="",
        comment="short discription of the entity",
    )

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
