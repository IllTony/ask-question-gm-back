import sys
from loguru import logger
from src.core.settings import settings


logger.remove(0)
logger.add(
    sys.stderr,
    format="<green>{time}</green> | <level>{level}</level> | {module} | {function} | <level>{message}</level>",
    level=settings.LOGGING_LEVEL,
    colorize=True,
)

if settings.LOG_TO_FILE == "TRUE":
    logger.add(
        "{}/log.txt".format(settings.LOG_DIR),
        rotation="10 MB",
        retention="30 days",
        format="{time} | {level} | {module} | {function} | {message}",
        level=settings.LOGGING_LEVEL,
        colorize=True,
    )


log = logger
