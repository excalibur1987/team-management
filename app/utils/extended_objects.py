import copy
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
        only: List[str] = None,
        **kwargs,
    ):
        self.only = only
        if self.only is not None:
            model_copy = copy.deepcopy(model)
            for k in model._schema.get("properties").keys():
                if k not in only:
                    del model_copy[k]
                    if k in model_copy.resolved:
                        del model_copy.resolved[k]
            model = model_copy
        super().__init__(
            model,
            allow_null=allow_null,
            skip_none=skip_none,
            as_list=as_list,
            **kwargs,
        )


class IndexedAttribute:
    def __init__(self, name, id) -> None:
        self.name = name
        self.id = id

    def __repr__(self) -> str:
        return self.name

    def default(self):
        return self.name

    def __eq__(self, o: object) -> bool:
        return isinstance(o, IndexedAttribute) and self.name == o.name


class SubscriptableEnum:

    __list: List

    def __init__(self, list_: List[str]) -> None:
        self.__list = []
        for idx, item in enumerate(list_):
            indexed_item = IndexedAttribute(item, idx)
            self.__list.append(indexed_item)
            setattr(self, item.upper().replace(" ", "_"), indexed_item)

    def __getitem__(self, i) -> IndexedAttribute:
        return (
            self.__list[i] if isinstance(i, int) else self.__list[self.__list.index(i)]
        )

    def get_items(self) -> List[IndexedAttribute]:
        return self.__list

    items = property(get_items)
