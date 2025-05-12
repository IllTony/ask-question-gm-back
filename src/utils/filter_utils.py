from copy import deepcopy
from typing import (
    Union,
    Type,
    get_origin,
    Dict,
    Optional,
    Tuple,
    get_args,
    Iterable,
    List,
)

from pydantic.fields import FieldInfo
from fastapi import HTTPException, status

from src.query_params.base_filter import BaseFilter

UNION_TYPES: List = [Union]


orm_operator_transformer = {
    "eq": lambda value: ("__eq__", value),
    "neq": lambda value: ("__ne__", value),
    "gt": lambda value: ("__gt__", value),
    "gte": lambda value: ("__ge__", value),
    "in": lambda value: ("in_", value),
    "isnull": lambda value: ("is_", None) if value is True else ("is_not", None),
    "lt": lambda value: ("__lt__", value),
    "lte": lambda value: ("__le__", value),
    "contains": lambda value: ("contains", value),
    "icontains": lambda value: ("icontains", value),
    "not": lambda value: ("is_not", value),
    "not_in": lambda value: ("not_in", value),
}


def split_field(field, delemiter="__"):
    """Разделяет поле для фильтрации на model и field по разделителю."""
    try:
        model_name, field_name = field.split(delemiter)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"field: {field}, {e}")
    return model_name, field_name


def _list_to_str_fields(Filter: Type[BaseFilter]):
    """Возвращает поля фильтра с аннотацией и параметрами."""
    ret: Dict[str, Tuple[Union[object, Type], Optional[FieldInfo]]] = {}
    for name, f in Filter.model_fields.items():
        if name not in ["sort_field", "search_value", "search_fields"]:
            field_info = deepcopy(f)
            annotation = f.annotation

            if get_origin(annotation) in UNION_TYPES:
                annotation_args: list = list(get_args(f.annotation))
                if type(None) in annotation_args:
                    annotation_args.remove(type(None))
                if len(annotation_args) == 1:
                    annotation = annotation_args[0]
            if annotation is list or get_origin(annotation) is list:
                if isinstance(field_info.default, Iterable):
                    field_info.default = ",".join(field_info.default)
                ret[name] = (str if f.is_required() else Optional[str], field_info)
            else:
                ret[name] = (f.annotation, field_info)
    return ret
