from fastapi import Query
from pydantic import Field

from src.schemas.base_schema import BaseOrjsonModel
from src.core.settings import settings


class Paginator(BaseOrjsonModel):
    page_size: int = Field(default=settings.PAGE_SIZE)
    page_number: int = Field(default=1)

    @property
    def offset(self):
        return self.page_size * (self.page_number - 1)


def get_paginator(
    page_size: int = Query(settings.PAGE_SIZE, alias="page[size]", ge=1),
    page_number: int = Query(1, alias="page[number]", ge=1),
):
    return Paginator(
        page_size=page_size,
        page_number=page_number,
    )
