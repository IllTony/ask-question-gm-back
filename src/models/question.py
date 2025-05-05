from uuid import UUID
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.mixins import ModelHistoryMixin, ActivityMixin


class Question(Base, ModelHistoryMixin, ActivityMixin):
    __tablename__ = "questions"

    number: Mapped[str] = mapped_column(String(10), nullable=True)
    question: Mapped[str] = mapped_column(String(5000), nullable=True)
    person: Mapped[str] = mapped_column(String(255), nullable=True)
    is_answered: Mapped[bool] = mapped_column(default=False, nullable=True)

    # relationship
    status: Mapped[list["QuestionFile"]] = relationship(lazy="selectin")


class QuestionFile(Base, ModelHistoryMixin, ActivityMixin):
    __tablename__ = "question_files"
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    path: Mapped[str] = mapped_column(String(255), nullable=True)
    question_id: Mapped[UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), nullable=True, default=None
    )
