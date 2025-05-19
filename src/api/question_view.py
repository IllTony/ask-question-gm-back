from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status


from src.services.question_service import QuestionService, get_question_service
from src.exceptions.service_exceptions import ServiceObjectNotCreated, ServiceFilenameOverflow, ServiceFileNotAdd


router = APIRouter()


@router.post(
    "",
    summary="Создание вопроса",
    status_code=status.HTTP_201_CREATED,
)
async def create_question(
    question_service: Annotated[QuestionService, Depends(get_question_service)],
    question: str = Form(),
    fio: str | None = Form(None),
    files: list[UploadFile] = File(default=[]),
):
    try:
        return await question_service.create_question(question, fio, files)
    except ServiceObjectNotCreated as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=exc.detail)
    except ServiceFilenameOverflow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Длинное имя файлы. Файлы не добавлены к вопросу. Вопрос был создан и направлен на рассмотрение",
        )
    except ServiceFileNotAdd:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутрення ошибка. Файлы не добавлены к вопросу. Вопрос был создан и направлен на рассмотрение",
        )
