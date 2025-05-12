import orjson
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseOrjsonModel(BaseModel):
    model_config = {"model_validate": orjson.loads, "model_dump": orjson_dumps}


class BaseTableRow(BaseOrjsonModel):
    id: UUID
    creator: Optional[str] = Field(exclude=True)
    modifier: Optional[str] = Field(exclude=True)


class BaseTable(BaseOrjsonModel):
    page: int
    size: int
    total: int
