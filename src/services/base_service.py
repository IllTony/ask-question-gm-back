from typing import Any, Sequence
from sqlalchemy import select, Select, Result, func, desc, column, cast, or_, String, sql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.query_params import Paginator
from src.core.logger import log
from src.utils.filter_utils import orm_operator_transformer


class BaseService:
    _model: Any
    _session: AsyncSession
    _search_models: dict
    _query_models: list[dict]
    _tables_joined: list[str] = []

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_obj_or_none(self, **filter_by) -> Any:
        query_result: Result = await self._session.execute(select(self._model).filter_by(**filter_by))
        return query_result.scalar_one_or_none()

    async def get_objects(self, **filter_by) -> Sequence:
        query: Select = select(self._model).filter_by(**filter_by)
        query_result: Result = await self._session.execute(query)
        return query_result.scalars().all()

    async def get_filtered_objects(
        self, response_type: str = "TABLE", paginator: Paginator | None = None, filter: Any | None = None, **filter_by
    ) -> Any:
        if response_type == "TABLE":
            pass

    async def create_object(self, **data) -> Any:
        try:
            new_obj = self._model(**data)
            self._session.add(new_obj)
            await self._session.commit()
            await self._session.refresh(new_obj)
            return new_obj
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Ошибка базы данных: Не удалость добавить данные в таблицу {}".format(self._model.__tablename__)
            elif isinstance(e, Exception):
                msg = "Неизвестная ошибка: Не удалость добавить данные в таблицу: {}".format(self._model.__tablename__)
            log.opt(exception=True).error(msg)
            return None

    async def update_object(self, updated_obj: Any, updated_data: dict) -> Any:
        try:
            for k, v in updated_data.items():
                setattr(updated_obj, k, v)
            await self._session.commit()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Ошибка базы данных: Не удалость добавить данные в таблицу {}".format(self._model.__tablename__)
            elif isinstance(e, Exception):
                msg = "Неизвестная ошибка: Не удалость добавить данные в таблицу: {}".format(self._model.__tablename__)
            log.opt(exception=True).error(msg)
            return None
        return updated_obj

    async def delete_object(self, deleted_obj: Any, delete_in_db: bool = False) -> Any:
        try:
            if not delete_in_db:
                if hasattr(deleted_obj, "is_active"):
                    deleted_obj.is_active = False
                else:
                    msg = "У объекта модели {} нет атрибута is_active".format(self._model.__tablename__)
                    log.opt(exception=True).error(msg)
                    raise AttributeError(msg)
            else:
                await self._session.delete(deleted_obj)
            await self._session.commit()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Ошибка базы данных: Не удалость удалить объект {} {}".format(
                    self._model.__tablename__, deleted_obj.id
                )
            elif isinstance(e, Exception):
                msg = "Неизвестная ошибка: Не удалость удалить объект: {} {}".format(
                    self._model.__tablename__, deleted_obj.id
                )
            log.opt(exception=True).error(msg)
        return None

    def create_prefilter_query(self, query: Select, filter: Any) -> Select:
        return query

    def create_select_query(
        self,
        mode: str = "NORMAL",
        is_joined: bool = False,
        paginator: Paginator | None = None,
        filter: Any | None = None,
    ) -> Select | None:
        if mode not in ("NORMAL", "COUNT"):
            log.error("Неизвестный режим {} для формирования запроса".format(mode))
            return None
        self._tables_joined = []
        if mode == "NORMAL":
            if is_joined:
                if self._query_models:
                    query = self._create_columns_query()
                    for query_model in self._query_models:
                        if query_model.get("table_alias"):
                            model_name = query_model.get("table_alias")
                        else:
                            model_name = query_model.get("model_name")
                        query = query.join(
                            model_name,
                            model_name.id == getattr(self._model, query_model.get("joined_key")),
                            isouter=True,
                        )
                        self._tables_joined.append(model_name)
                else:
                    query = select(self._model.__table__.columns)
            else:
                query = select(self._model)
            if filter:
                query = self.create_filter_query(query, filter, mode=mode)
            if paginator:
                query = self.create_offset_query(query, paginator)
        elif mode == "COUNT":
            query = select(func.count()).select_from(self._model)
            if filter:
                query = self.create_filter_query(query, filter, mode=mode)
        return query

    def create_offset_query(self, query: Select, paginator: Paginator) -> Select:
        try:
            if paginator.page_size is not None:
                query = query.limit(paginator.page_size)
                query = query.offset(paginator.offset)
            return query
        except Exception:
            log.opt(exception=True).error(
                "Неизвестная ошибка: Не удалось сформировать запрос для фильтрации для таблицы {}".format(
                    self._model.__tablename__
                )
            )
        return query

    def create_filter_query(
        self,
        query: Select,
        filter: Any,
        mode: str = "NORMAL",
    ) -> Select:
        try:
            if mode == "NORMAL":
                if filter.sort_field:
                    query = self.create_sort_query(query, filter.sort_field)
            if filter.search_fields:
                query = self.create_search_query(query, filter.search_fields, filter.search_value)
            for field_name, field_value in filter.filtering_fields:
                if isinstance(field_value, sql.selectable.Exists):
                    query = query.filter(field_value)
                    continue
                if "__" in field_name:
                    field_name, operator = field_name.split("__")
                    operator, value = orm_operator_transformer[operator](field_value)
                    field_value = value
                else:
                    operator = "__eq__"
                if operator in ["contains", "icontains"]:
                    model_field = cast(getattr(self._model, field_name), String)
                else:
                    if field_name in self._model.__table__.columns.keys():
                        model_field = getattr(self._model, field_name)
                    else:
                        for item in self._filter_instance:
                            if item.get("filter_field") == field_name:
                                model_field = getattr(item.get("model"), item.get("field"))
                query = query.filter(getattr(model_field, operator)(field_value))
            return query
        except Exception as ex:
            print(ex)
            log.opt(exception=True).error(
                "Неизвестная ошибка: Не удалось сформировать запрос для фильтрации для таблицы {}".format(
                    self._model.__tablename__
                )
            )
            return query

    def create_search_query(self, query: Select, search_field: str, search_value: str) -> Select:
        try:
            if search_field.endswith(","):
                search_field = search_field[:-1]
            search_field_list = search_field.split(",")
            search_filters = []
            for field in search_field_list:
                if "__" in field:
                    if field.split("__")[0] in self._search_models.keys():
                        if self._search_models.get(field.split("__")[0]).get("table_alias"):
                            model_name = "table_alias"
                        else:
                            model_name = "model_name"

                        if self._search_models.get(field.split("__")[0]).get("table_chain"):
                            table_chain = self._search_models.get(field.split("__")[0]).get("table_chain")
                            to_table = self._model
                            for table_join in table_chain:
                                if table_join.get("from_model") not in self._tables_joined:
                                    query = query.join(
                                        table_join.get("from_model"),
                                        table_join.get("from_model").id
                                        == getattr(
                                            to_table,
                                            "{}".format(table_join.get("joined_key")),
                                        ),
                                        isouter=True,
                                    )
                                    self._tables_joined.append(table_join.get("from_model"))
                                    to_table = table_join.get("from_model")
                        else:
                            if self._search_models.get(field.split("__")[0]).get(model_name) not in self._tables_joined:
                                query = query.join(
                                    self._search_models.get(field.split("__")[0]).get(model_name),
                                    (
                                        self._search_models.get(field.split("__")[0]).get(model_name).id
                                        == getattr(
                                            self._model,
                                            "{}_id".format(field.split("__")[0]),
                                        )
                                    ),
                                    isouter=True,
                                )
                                self._tables_joined.append(
                                    self._search_models.get(field.split("__")[0]).get(model_name)
                                )
                        search_filters.append(
                            cast(
                                getattr(
                                    self._search_models.get(field.split("__")[0]).get(model_name),
                                    field.split("__")[1],
                                ),
                                String,
                            ).icontains(search_value)
                        )
                else:
                    search_filters.append(cast(getattr(self._model, field), String).icontains(search_value))
            return query.filter(or_(*search_filters))
        except Exception:
            log.opt(exception=True).error(
                "Неизвестная ошибка: Не удалось сформировать запрос поиска для таблицы {}".format(
                    self._model.__tablename__
                )
            )
            return query

    def create_sort_query(self, query: Select, sort_field: str) -> Select:
        try:
            if "-" in sort_field:
                sort_field = sort_field.replace("-", "")
                if "__" in sort_field:
                    if self._search_models.get(sort_field.split("__")[0]).get("table_alias"):
                        model_name = "table_alias"
                    else:
                        model_name = "model_name"
                    new_query = query.order_by(
                        desc(
                            getattr(
                                self._search_models.get(sort_field.split("__")[0]).get(model_name),
                                sort_field.split("__")[1],
                            )
                        )
                    )
                else:
                    new_query = query.order_by(desc(column(sort_field)))
            else:
                if "__" in sort_field:
                    if self._search_models.get(sort_field.split("__")[0]).get("table_alias"):
                        model_name = "table_alias"
                    else:
                        model_name = "model_name"
                    new_query = query.order_by(
                        getattr(
                            self._search_models.get(sort_field.split("__")[0]).get(model_name),
                            sort_field.split("__")[1],
                        ),
                    )
                else:
                    new_query = query.order_by(column(sort_field))
            return new_query
        except Exception:
            log.opt(exception=True).error(
                "Неизвестная ошибка: Не удалось сформировать запрос сортировки для таблицы {}".format(
                    self._model.__tablename__
                )
            )
            return query

    def _create_columns_query(self):
        add_columns = []
        for query_model in self._query_models:
            for joined_col in query_model.get("joined_cols"):
                if query_model.get("table_alias"):
                    add_columns.append(
                        getattr(query_model.get("table_alias"), joined_col.get("col_name")).label(
                            joined_col.get("label")
                        )
                    )
                else:
                    add_columns.append(
                        getattr(query_model.get("model_name"), joined_col.get("col_name")).label(
                            joined_col.get("label")
                        )
                    )
        query = select(self._model.__table__.columns, *add_columns)
        return query

    def _fill_characters(self, value: str, size: int, char: str = "0", direction: str = "left") -> str:
        result = ""
        for _ in range(0, size - len(value)):
            result += char
        return result + value if direction == "left" else value + result
