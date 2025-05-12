from fastapi import Query

from src.query_params.base_filter import BaseFilter


class QuestionFilter(BaseFilter):
    pass


def get_question_filter(
    search_fields: str | None = Query(None, alias="search[fields]"),
    search_value: str | None = Query(None, alias="search[value]", ge=1),
    sort_field: str | None = Query("-created_at", alias="sort"),
):
    return QuestionFilter(search_fields=search_fields, search_value=search_value, sort_field=sort_field)
