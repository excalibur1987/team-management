import sys
import traceback
from datetime import datetime
from linecache import getline
from typing import TYPE_CHECKING

from flask.globals import current_app
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import INTEGER, DateTime, Integer, String

from app.database import BaseModel
from app.utils import g

if TYPE_CHECKING:
    from app.apis.v1.users.models import Session, User


class ErrorLog(BaseModel):
    __tablename__ = "error_log"
    code = Column(String, comment="Application Error identifier code")

    user_id = Column(Integer, ForeignKey("users.id"), comment="logged in user")
    user: "User" = relationship("User", foreign_keys=[user_id], uselist=False)

    message = Column(String, comment="error message")
    stack_trace = Column(String, comment="error stack trace")

    date_added = Column(
        DateTime(True),
        nullable=False,
        default=lambda: datetime.now(tz=current_app.config["TZ"]),
        comment="row timestamp",
    )

    added_by_id = Column(INTEGER, ForeignKey("users.id"))
    added_by: "User" = relationship("User", foreign_keys=[added_by_id])

    session_id = Column(INTEGER, ForeignKey("sessions.id"))
    session: "Session" = relationship("Session", foreign_keys=[session_id])

    def __init__(self, e: Exception) -> None:
        exc_type, exc_value, exc_tb = sys.exc_info()
        trace = traceback.format_tb(exc_tb)
        trace = list(
            filter(
                lambda x: (
                    "\\lib\\" not in x and "/lib/" not in x and __name__ not in x
                ),
                trace,
            )
        )
        ex_type = exc_type.__name__
        ex_line = exc_tb.tb_lineno
        ex_file = exc_tb.tb_frame.f_code.co_filename
        ex_message = str(exc_value)
        line_code = ""
        try:
            line_code = getline(ex_file, ex_line).strip()
        except Exception:
            pass

        trace.insert(
            0,
            f'File "{ex_file}", line {ex_line}, line_code: {line_code} , ex: {ex_type} {ex_message}',
        )
        trace_str = "\n".join(list(map(str, trace)))

        self.code = getattr(e, "code", None)
        self.message = getattr(e, "message", getattr(e, "msg", str(e)))
        self.stack_trace = trace_str
        self.added_by_id = getattr(getattr(g, "identity", None), "id", None)
        self.session_id = getattr(getattr(g, "session", None), "id", None)
