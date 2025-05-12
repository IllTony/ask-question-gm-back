from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Setting(BaseSettings):
    """
    Класс настроек
    """

    PROJECT_NAME: str = Field("ask-question", alias="PROJECT_NAME")

    # Настройки для базы данных postgres
    DB_HOST: str = Field("localhost", alias="DB_HOST")
    DB_PORT: str = Field("5475", alias="DB_PORT")
    DB_NAME: str = Field("question_db", alias="DB_NAME")
    DB_USER: str = Field("question_user", alias="DB_USER")
    DB_PASSWORD: str = Field("123qwe", alias="DB_PASSWORD")
    DB_ECHO: bool = False

    # Настройка для загрузки файлов
    FILE_UPLOAD: str = Field("/usr/src/app/media", alias="FILE_UPLOAD")

    # Настройка origin
    ALLOWED_HOSTS: str = Field(
        "http://localhost,http://localhost:8000,http://localhost:5173,",
        alias="ALLOWED_HOSTS",
    )
    # Настройки JWT
    JWT_SECRET_KEY: str = Field("secret", alias="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", alias="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRATION: int = Field(15, alias="ACCESS_LIFETIME")
    REFRESH_TOKEN_EXPIRATION: int = Field(1440, alias="REFRESH_LIFETIME")

    # Пагинация
    PAGE_SIZE: int = Field(50, alias="PAGE_SIZE")

    # Логгирование
    LOGGING_LEVEL: str = Field("DEBUG", alias="LOGGING_LEVEL")
    LOG_TO_FILE: str = Field("TRUE", alias="LOG_TO_FILE")
    LOG_DIR: str = Field("./logs", alias="LOG_DIR")

    @property
    def ALLOWED_HOSTS_LIST(self) -> list:
        return [] if self.ALLOWED_HOSTS == "" else self.ALLOWED_HOSTS.split(",")

    @property
    def database_url_async(self):
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}".format(
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            db=self.DB_NAME,
        )

    @property
    def database_url_sync(self):
        return "postgresql://{user}:{password}@{host}:{port}/{db}".format(
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            db=self.DB_NAME,
        )


settings = Setting()
