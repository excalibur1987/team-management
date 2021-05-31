import re
from typing import TYPE_CHECKING, Any, List, Union

from flask import current_app
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BOOLEAN, Integer, String
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import BaseModel, DatedModel, db
from app.exceptions import UserExceptions
from app.utils.file_handler import FileHandler

if TYPE_CHECKING:
    from ...entities.models import Entity
    from ...roles.models import Role
    from ._Session import Session  # NOQA

    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property


class PasswordHelper:
    password: str

    def __init__(self, password) -> None:
        self.password = password

    def __eq__(self, o: object) -> bool:
        assert isinstance(o, str)
        equality: bool = check_password_hash(self.password, o)
        return equality


class User(BaseModel, DatedModel):
    """Holds users' data"""

    __tablename__ = "users"
    username = Column(String, nullable=False, unique=True, comment="User's identifier")
    active = Column(
        "is_active",
        BOOLEAN(),
        nullable=False,
        server_default=cast(1, BOOLEAN),
        comment="Denotes active users",
    )

    _password = Column("password", String, nullable=False, comment="Password hash")

    # User identifiers
    email = Column(
        String, nullable=True, unique=True, comment="User's personal unique email"
    )

    # meta data
    _photo = Column("photo", String, nullable=True, comment="User's avatar url")
    phone = Column(String, nullable=True, comment="Contact number")

    # User information
    first_name = Column(String, nullable=False, comment="First Name")
    last_name = Column(String, nullable=False, server_default="", comment="Last Name")

    # Uncomment to if you want to add manager employee relations
    # manager_id = Column(String, nullable=True)
    # manager: "User" = relationship(
    #     "User", foreign_keys=[manager_id], lazy=True, uselist=False
    # )

    # employees: List["User"] = relationship(
    #     "User",
    #     lazy=True,
    #     uselist=True,
    #     primaryjoin="User.user_id==foreign(User.manager_id)",
    # )

    # Relationships

    # Define the relationship to Role via UserRoles
    roles = relationship("Role", secondary="user_roles")
    # user sessions
    sessions = relationship(
        "Session", order_by="Session.created_at.asc()", uselist=True
    )

    token = None

    def set_password(self, val: str):
        regx = re.compile(current_app.config["PASSWORD_RULE"])
        if not regx.match(val):
            raise UserExceptions.password_check_invalid()
        self._password = generate_password_hash(val)

    def get_password(self):
        return PasswordHelper(self._password)

    password = property(get_password, set_password)

    def get_photo(self):
        return (
            self.__photo_handler
            if getattr(self, "__photo_handler", None) is not None
            else FileHandler(url=self._photo)
            if self._photo
            else None
        )

    def set_photo(self, val: FileHandler):
        self.__photo_handler = val
        self._photo = getattr(val, "url", None)

    photo = property(get_photo, set_photo)

    def __init__(
        self,
        username: str,
        password: str,
        password_check: str,
        active: bool = True,
        email: str = None,
        photo: "FileHandler" = None,
        phone: str = None,
        first_name: str = "",
        last_name: str = "",
        **kwargs,
    ) -> None:
        if password != password_check:
            raise UserExceptions.password_check_invalid()
        self.username = username
        self.password = password
        self.active = active
        self.email = email
        self.photo = photo
        self.phone = phone
        self.first_name = first_name
        self.last_name = last_name

    def __setattr__(self, name: str, value: Any) -> None:
        """intercept setting of password"""
        if name == "password":
            regx = re.compile(current_app.config["PASSWORD_RULE"])
            if not regx.match(value):
                raise UserExceptions.password_check_invalid()
            self._password = value
        elif name == "photo":
            assert isinstance(value, FileHandler)
            self._photo = value.url
        else:
            super(User, self).__setattr__(name, value)

    @hybrid_property
    def photo(self) -> Union[FileHandler, None]:
        return FileHandler(url=self._photo) if self._photo else None

    @hybrid_property
    def password(self) -> PasswordHelper:
        """password proxy helper"""
        return PasswordHelper(self._password)

    @hybrid_property
    def name(self) -> str:
        """concatenates user's name"""
        return f"{self.first_name} {self.last_name}"

    def add_roles(self, roles: Union[List["Role"], "Role"]):
        """add roles to user

        Args:
            roles: A list of or a single role instances
        """
        from ._UserRoles import UserRoles

        new_roles = [
            UserRoles(user=self, role=role)
            for role in (roles if isinstance(roles, list) else [roles])
        ]

        db.session.add_all(new_roles)

    def delete(self, persist=False):
        """Delete user's record"""
        if self.photo:
            self.photo.delete()
        super().delete(persist=persist)

    def add_entity(self, entity: "Entity", create: bool = False, edit: bool = False):
        from ._UserEntityPermission import UserEntityPermission

        permission = UserEntityPermission(
            entity=entity, user=self, create=create, edit=edit
        )
        db.session.add(permission)
        db.session.commit()
