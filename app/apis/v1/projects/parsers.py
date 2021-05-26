from datetime import date

import werkzeug
from dateutil.parser import parse
from flask_restx.reqparse import RequestParser

from app.utils.parsers import DateParserType, offset_parser

query_parser = offset_parser.copy().add_argument(
    "title",
    type=str,
    ignore=True,
    location="args",
).add_argument(
    "completed",
    dest="is_completed",
    type=str,
    ignore=True,
    location="args",
).add_argument(
    "public",
    dest="is_public",
    type=str,
    ignore=True,
    default=True,
    location="args",
).add_argument(
    "start",
    dest="start_date",
    type=parse,
    ignore=True,
    location="args",
)


project_parser = RequestParser()
project_parser.add_argument(
    "title",
    type=str,
    required=True,
    location="form",
).add_argument("description", type=str, required=True, location="form",).add_argument(
    "public",
    type=bool,
    required=True,
    location="form",
).add_argument(
    "logo",
    type=werkzeug.datastructures.FileStorage,
    location="files",
).add_argument(
    "startDate",
    dest="start_date",
    type=DateParserType(),
    help=date.today().isoformat(),
    required=True,
    location="form",
).add_argument(
    "endDate",
    dest="end_date",
    type=DateParserType(),
    help=date.today().isoformat(),
    required=True,
    location="form",
)
