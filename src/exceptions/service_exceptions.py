class ServiceException(BaseException):
    detail = "Внутрення ошибка сервера"

    def __init__(self, detail: str | None = None) -> None:
        super().__init__()
        if detail:
            self.detail = detail


class ServicePermissionDenied(ServiceException):
    detail = "Доступ запрещен"


class ServiceObjectNotCreated(ServiceException):
    detail = "Ошибка при создании объекта"


class ServiceObjectNotUpdated(ServiceException):
    detail = "Ошибка при обновлении объекта"


class ServiceObjectNotFound(ServiceException):
    detail = "Объект не найден"


class ServiceInvlidCredentials(ServiceException):
    detial = "Неверное имя пользователя или пароль"


class ServiceUserDeactivated(ServiceException):
    detail = "Пользователь деактивирован"


class ServiceBadRequest(ServiceException):
    detail = "Неверный запрос."


class ServiceFilenameOverflow(ServiceException):
    detail = "Имя файла слишком большое."


class ServiceFileNotAdd(ServiceException):
    detail = "Не удалось добавить файл"
