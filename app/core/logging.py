import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.constants import LogEvent


LOG_DIRECTORY = Path("logs")
APPLICATION_LOG_FILE = LOG_DIRECTORY / "supportiq.log"
ERROR_LOG_FILE = LOG_DIRECTORY / "errors.log"


class JsonFormatter(logging.Formatter):

    STANDARD_ATTRIBUTES = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "taskName",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key not in self.STANDARD_ATTRIBUTES:
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(
                record.exc_info
            )

        return json.dumps(
            payload,
            default=str,
            ensure_ascii=False,
        )


class MaxLevelFilter(logging.Filter):

    def __init__(self, maximum_level: int) -> None:
        super().__init__()
        self.maximum_level = maximum_level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= self.maximum_level


def configure_logging() -> None:
    LOG_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    root_logger.handlers.clear()

    formatter = JsonFormatter()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    application_handler = logging.FileHandler(
        APPLICATION_LOG_FILE,
        encoding="utf-8",
    )
    application_handler.setLevel(logging.INFO)
    application_handler.addFilter(
        MaxLevelFilter(logging.WARNING)
    )
    application_handler.setFormatter(formatter)

    error_handler = logging.FileHandler(
        ERROR_LOG_FILE,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(application_handler)
    root_logger.addHandler(error_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_event(
    logger: logging.Logger,
    level: int,
    event: LogEvent | str,
    message: str,
    **context: Any,
) -> None:
    logger.log(
        level,
        message,
        extra={
            "event": str(event),
            **context,
        },
    )
