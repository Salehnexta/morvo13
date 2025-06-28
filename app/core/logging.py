"""
Logging configuration for the application.
"""

import json
import logging
import sys
from types import FrameType
from typing import Any, Callable, Dict, Union

from loguru import logger

from app.core.config.settings import settings


class InterceptHandler(logging.Handler):
    """
    Intercept standard logging and redirect to loguru.
    See: https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        level: Union[str, int]
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame: FrameType | None = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class JsonFormatter:
    """
    JSON formatter for structured logging.
    """

    def __init__(self) -> None:
        self.format_keys = [
            "level",
            "timestamp",
            "message",
            "module",
            "function",
            "line",
            "exception",
            "trace_id",
        ]

    def __call__(self, record: dict[str, Any]) -> str:
        log_record = {key: record.get(key) for key in self.format_keys if key in record}
        # Add any extra fields to the log record
        log_record.update(record.get("extra", {}))
        return json.dumps(log_record)


def setup_logging() -> None:
    """
    Configure loguru logger.
    """
    # Remove default loguru handler
    logger.remove()

    # Determine log format based on settings
    log_format: Union[JsonFormatter, str] = (
        JsonFormatter()
        if settings.JSON_LOGS
        else (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
    )

    # Add console handler
    logger.add(
        sys.stderr,
        format=log_format,  # type: ignore
        level=settings.LOG_LEVEL,
        serialize=settings.JSON_LOGS,
    )

    # Optional rotating file handler for production debugging
    if settings.LOG_TO_FILE:
        import os
        from pathlib import Path
        from loguru._handler import Handler
        log_path = Path(settings.LOG_FILE_PATH)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_path,
            rotation="10 MB",
            retention="14 days",
            format=log_format,  # type: ignore
            level=settings.LOG_LEVEL,
            serialize=settings.JSON_LOGS,
        )

    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Update logging levels for some noisy loggers
    for logger_name in ("uvicorn", "uvicorn.error", "fastapi"):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]

    # Set uvicorn access logger
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]

    logging.info(f"Logging initialized. Level: {settings.LOG_LEVEL}, JSON: {settings.JSON_LOGS}")
