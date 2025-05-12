from functools import lru_cache
from uuid import UUID
import datetime as dt

from fastapi import Depends, UploadFile
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import get_async_session
from src.core.logger import log
from src.models import User, Question, QuestionFile
from src.services.base_service import BaseService
from src.query_params import QuestionFilter, Paginator
from src.utils.file_utils import FileUtils
from src.exceptions.service_exceptions import (
    ServiceObjectNotCreated,
    ServiceObjectNotUpdated,
    ServiceFilenameOverflow,
    ServiceFileNotAdd,
)


class QuestionService(BaseService):
    _model = Question

    async def get_question(self, question_id: UUID | str, current_user: User):
        pass

    async def get_questions(
        self,
        response_type: str,
        current_user: User,
        filter: QuestionFilter | None = None,
        paginator: Paginator | None = None,
    ):
        pass

    async def create_question(self, question: str, fio: str | None = None, files: list[UploadFile] | None = None):
        data = {"question": question}
        if fio:
            data.update({"person": fio})

        number = await self._create_next_num()
        data.update({"number": number})

        new_question = await self.create_object(**data)
        if new_question is None:
            raise ServiceObjectNotCreated("Не удалось создать в вопрос")

        for file in files:
            if len(file.filename) > 125:
                log.error(
                    "Не удалось создать файл, имя файла слишком большое: {}".format(file.filename),
                )
                raise ServiceFilenameOverflow(
                    detail="Имя файла слишком большое: {}".format(file.filename),
                )
            folder_path = FileUtils.create_folder_path("QUESTION", str(dt.datetime.now().year))
            file_data = FileUtils.get_file_data(file.filename, folder_path)

            try:
                question_file = QuestionFile(
                    name=file_data.get("filename"), path=file_data.get("path"), question_id=new_question.id
                )
                self._session.add(question_file)
                await self._session.commit()
                await self._session.refresh(question_file)
                FileUtils.file_upload(file, question_file.path)
            except Exception:
                raise ServiceFileNotAdd("Не удалось добавить файлы к вопросу")
        return question

    async def update_question(
        self,
        current_user: User,
        question_id: str | UUID,
        question: str,
        fio: str,
        is_answered: bool | None = None,
        files: list[UploadFile] | None = None,
    ):
        pass

    async def set_question_answered(self, current_user: User, question_id: UUID | str):
        pass

    async def delete_question(self, current_user: User, question_id: UUID | str):
        pass

    async def _create_next_num(self):
        current_year = dt.datetime.now().year

        # Получаем последний используемый номер
        last_num_res = await self._session.execute(select(Question.number).order_by(desc(Question.created_at)).limit(1))
        last_num_res = last_num_res.scalars().one_or_none()

        # Генерируем номер
        if last_num_res is None:
            return "00001-{}".format(current_year)
        else:
            last_question_year = last_num_res.split("-")[1]
            if last_question_year == str(current_year):
                number = int(last_num_res.split("-")[0]) + 1
                number_str = self._fill_characters(value=str(number), size=5)
                return "{}-{}".format(number_str, current_year)
            else:
                return "00001-{}".format(current_year)


@lru_cache()
def get_question_service(
    session: AsyncSession = Depends(get_async_session),
) -> QuestionService:
    return QuestionService(session)
