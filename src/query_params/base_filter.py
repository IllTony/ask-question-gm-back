from typing import Optional
from src.schemas.base_schema import BaseOrjsonModel


class BaseFilter(BaseOrjsonModel):
    """
    Базовый класс фильтрации для наследования фильтров

    Arguments:
        BaseOrjsonModel -- базовая модель
    """

    search_fields: Optional[str] = None
    search_value: Optional[str] = None
    sort_field: Optional[str] = None

    class Constants:
        prefix: Optional[str] = None

    @property
    def filtering_fields(self):
        """
        Возвращает поля для фильтрации, которые были получены в запросе, исключая поле поиска и сортировки
        """
        fields = self.model_dump(
            exclude_none=True,
            exclude_unset=True,
            exclude={"search_fields", "search_value", "sort_field"},
        )
        return fields.items()
