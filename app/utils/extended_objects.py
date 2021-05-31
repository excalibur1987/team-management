from functools import wraps
from typing import Callable, List, Union

from flask_restx import Model, OrderedModel, fields
from flask_restx.namespace import Namespace

from app.database import BaseModel

from .parsers import offset_parser


class ExtendedNameSpace(Namespace):
    def serialize_multi(
        self,
        restx_model: Union[Model, OrderedModel],
        db_model: BaseModel,
        description="",
    ):
        extended_model = self.model(
            f"{restx_model.name}s",
            {
                "count": fields.Integer(),
                "data": fields.Nested(restx_model, as_list=True),
                "limit": fields.Integer(),
                "offset": fields.Integer(),
            },
        )

        def wrapper(fn: Callable):
            @wraps(fn)
            @self.marshal_with(extended_model)
            @self.response(200, description, model=extended_model)
            def wrapped(*args, **kwargs):
                args_ = offset_parser.parse_args()
                result: List[BaseModel] = fn(*args, **kwargs)

                return {
                    "count": db_model.query.count(),
                    "limit": args_.get("limit", 10) or 10,
                    "offset": args_.get("offset", 0) or 0,
                    "data": result,
                }

            return wrapped

        return wrapper


class Nested(fields.Nested):
    def __init__(
        self,
        model,
        allow_null=False,
        skip_none=False,
        as_list=False,
        only: List[str] = [],
        **kwargs,
    ):
        super().__init__(
            model, allow_null=allow_null, skip_none=skip_none, as_list=as_list, **kwargs
        )
        self.only = kwargs.get("only", [])

    def output(self, key, obj, ordered=False, **kwargs):
        value = fields.get_value(key if self.attribute is None else self.attribute, obj)
        if value is None:
            if self.allow_null:
                return None
            elif self.default is not None:
                return self.default
        if len(self.only) == 0:
            return fields.marshal(
                value, self.nested, skip_none=self.skip_none, ordered=ordered
            )
        new_value = {}
        if isinstance(value, dict):
            new_value = dict((key, new_value.get(key)) for key in self.only)
        else:
            new_value = dict((key, getattr(new_value, key)) for key in self.only)
        return fields.marshal(
            new_value, self.nested, skip_none=self.skip_none, ordered=ordered
        )
