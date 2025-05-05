from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


from src.models.base import Base
from src.models.mixins import ModelHistoryMixin
from src.utils.password import check_password


class User(Base, ModelHistoryMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(default=True)
    is_stuff: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)

    def check_password(self, password: str) -> bool:
        return check_password(self.password, password)
