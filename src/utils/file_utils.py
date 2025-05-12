import os
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from src.core.settings import settings
from src.core.logger import log
from src.exceptions.service_exceptions import ServiceObjectNotCreated


class FileUtils:
    """Класс для загрузки файлов"""

    @staticmethod
    def create_folder_path(folder_name: str | None = None, folder_year: str | None = None):
        path = settings.FILE_UPLOAD
        if folder_name:
            path = "{}/{}".format(path, folder_name)
        if folder_year:
            path = "{}/{}".format(path, folder_year)
        try:
            folder_path = Path(os.path.join(path))
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
        except Exception:
            log.error(
                "Не удалось создать директорию для файла {}".format(folder_path),
            )
            raise ServiceObjectNotCreated(
                detail="Не удалось создать директорию для файла {}".format(folder_path),
            )
        return folder_path

    @staticmethod
    def file_upload(file: UploadFile, path):
        try:
            with open(path, "wb+") as file_object:
                file_object.write(file.file.read())
        except Exception:
            log.error(
                "Не удалось сохранить файл {} в директорию {}".format(file, path),
            )
            raise ServiceObjectNotCreated(
                detail="Не удалось сохранить файл {} в директорию {}".format(file, path),
            )

    @staticmethod
    def get_file_data(filename, path) -> dict:
        unique_name = uuid4().hex
        filename, file_extension = os.path.splitext(filename)
        path = os.path.join(
            path,
            "{}-{}{}".format(
                filename,
                unique_name,
                file_extension,
            ),
        )

        return {
            "filename": filename,
            "unique_name": f"{filename}_{unique_name}{file_extension}",
            "path": path,
        }
