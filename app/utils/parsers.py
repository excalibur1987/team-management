from datetime import date, datetime
from typing import Any, Union

from dateutil.parser import ParserError, parse
from flask_restx.reqparse import RequestParser

offset_parser = RequestParser()
offset_parser.add_argument("offset", type=int, location="args", required=False)
offset_parser.add_argument("limit", type=int, location="args", required=False)


class DateParserType(object):
    time: bool

    def __init__(self, time: bool = False) -> None:
        super().__init__()
        self.time = time

    def __call__(self, value: Any) -> Union[date, datetime]:
        value = str(value)
        if value.isnumeric():
            try:
                casted = datetime.fromtimestamp(float(value))
            except ValueError:
                casted = datetime.fromtimestamp(float(value) / 1000)
        else:
            try:
                casted = datetime.strptime(value, "%y-%m-%d")
            except ValueError:
                casted = parse(value, yearfirst=True)
            except ParserError:
                casted = parse(value, datefirst=True)
        return casted if self.time else casted.date()
