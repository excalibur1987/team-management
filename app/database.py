from datetime import datetime
from typing import TYPE_CHECKING, Type, TypeVar, Union

from flask.globals import current_app
from flask_jwt_extended import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model
from sqlalchemy import Column, and_
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.schema import ForeignKey, MetaData, Table
from sqlalchemy.sql.sqltypes import INTEGER, DateTime

from app.exceptions import InvalidUsage

if TYPE_CHECKING:
    from app.apis.v1.users.models import User  # NOQA


metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

T = TypeVar("T")


class ExtendedModel(Model):
    __table__: Table
    __tablename__: str
    id = Column(
        INTEGER, primary_key=True, nullable=False, comment="Unique row identifier"
    )
    date_updated: "Column[datetime]"

    def update(self, ignore_none: bool = False, **kwargs):
        for key in kwargs.keys():
            if not ignore_none or kwargs.get(key) is not None:
                setattr(self, key, kwargs.get(key))
        db.session.commit()

    @classmethod
    def get(cls: T, id: int = None, **kwargs) -> Union[T, None]:
        """Gets class instance using id or named attributes
        Args:
            id (int, optional): User id.
            kwargs: named arguments must be an attribute of the class
        Returns:
            An instance of the class
        """
        for arg in kwargs.keys():
            assert hasattr(cls, arg)
        result: T = (
            db.session.query(cls)
            .filter(
                and_(
                    or_(getattr(cls, "id") == id, id == None),
                    *[
                        getattr(cls, arg) == val
                        for arg, val in kwargs.items()
                        if hasattr(cls, arg)
                    ],
                )
            )
            .one_or_none()
        )
        return result

    def __iter__(self):
        for key in self.__dict__:
            if not key.startswith("_"):
                yield key, getattr(self, key)

    def save(self, persist=True):
        """Saves instance to database

        Args:
            persist (bool, optional): Commit changes. Defaults to True.
        """
        db.session.add(self)
        if persist:
            db.session.commit()

    def delete(self, persist=False):
        """Deletes instance from database

        Args:
            persist (bool, optional): Commit changes. Defaults to False.
        """
        db.session.delete(self)
        if persist:
            db.session.commit()


db = SQLAlchemy(model_class=ExtendedModel, metadata=metadata)


class ViewModel(object):
    __table_args__ = {"info": dict(is_view=True)}
    is_view = True

    @classmethod
    def get_ddl(cls):
        sql = "select pg_get_viewdef(to_regclass(:view))"
        return (
            "CREATE OR REPLACE VIEW public.v_user_view\nAS\n"
            + f"{db.session.execute(sql, params={'view':cls.__tablename__}).scalar()}"
        )

    def delete(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError


if TYPE_CHECKING:
    from flask_sqlalchemy.model import Model

    BaseModel: Type[ExtendedModel] = db.make_declarative_base(ExtendedModel)
else:
    BaseModel = db.Model


class DatedModel(object):
    @declared_attr
    def date_added(self):
        return Column(
            DateTime(True),
            nullable=False,
            default=lambda: datetime.now(tz=current_app.config["TZ"]),
            comment="row timestamp",
        )

    @declared_attr
    def date_updated(self):
        return Column(
            DateTime(True),
            nullable=False,
            default=lambda: datetime.now(tz=current_app.config["TZ"]),
            comment="timestamp for last updated",
        )

    @declared_attr
    def added_by_id(self):
        return Column(INTEGER, ForeignKey("users.id"))

    @declared_attr
    def added_by(self):
        return relationship("User", foreign_keys=f"{self.__name__}.added_by_id")

    @declared_attr
    def updated_by_id(self):
        return Column(INTEGER, ForeignKey("users.id"), comment="fk for user's table")

    @declared_attr
    def updated_by(self):
        return relationship("User", foreign_keys=f"{self.__name__}.updated_by_id")

    def __init__(self, **kwargs) -> None:

        if not current_user and not kwargs.get("added_by_id", None):
            raise InvalidUsage.user_not_found()
        self.added_by_id = kwargs.get("added_by", current_user.id)

    def update(self, ignore_none: bool = False, **kwargs):
        for key in kwargs.keys():
            if not ignore_none or kwargs.get(key) is not None:
                setattr(self, key, kwargs.get(key))
        self.date_updated = datetime.now(tz=current_app.config["TZ"])
        self.updated_by_id = kwargs.get("updated_by_id", current_user.id)
        db.session.commit()


class CancelableModel(object):

    cancelled_at = Column(
        DateTime(True), nullable=True, comment="timestamp for cancellation of record"
    )

    @declared_attr
    def cancelled_by_id(cls):
        return Column(INTEGER, ForeignKey("users.id"), comment="fk for user's table")

    def cancel(self):

        if not current_user:
            raise InvalidUsage.user_not_found()
        self.cancelled = True
        self.cancelled_by_id = current_user.id
        self.date_cancelled = datetime.now(tz=current_app.config["TZ"])
        db.session.commit()


def ArrayList(_type, dimensions=1):
    # https://stackoverflow.com/a/29859182
    class MutableList(Mutable, list):
        @classmethod
        def coerce(cls, key, value):
            if not isinstance(value, cls):
                return cls(value)
            else:
                return value

    def _make_mm(mmname):
        def mm(self, *args, **kwargs):
            try:
                retval = getattr(list, mmname)(self, *args, **kwargs)
            finally:
                self.changed()
            return retval

        return mm

    modmethods = [
        "append",
        "clear",
        "copy",
        "count",
        "extend",
        "index",
        "insert",
        "pop",
        "remove",
        "reverse",
        "sort",
    ]

    for m in modmethods:
        setattr(MutableList, m, _make_mm(m))

    return MutableList.as_mutable(ARRAY(_type, dimensions=dimensions))
