"""Structured logging system powered by Loguru."""

import logging
import sys
from loguru import logger
from app.core.config import settings


class InterceptHandler(logging.Handler):
    """Intercept standard logging messages and redirect to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Process log record through Loguru."""
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            if frame.f_back:
                frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """Configure Loguru structured logging for the backend application."""
    # Remove existing default loggers
    logger.remove()

    # Add stdout handler with colorized log formatting
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        enqueue=True,
        backtrace=True,
        level=settings.LOG_LEVEL,
        format=log_format,
        colorize=True,
    )

    # Intercept standard library logging (uvicorn, fastapi, sqlalchemy)
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for _log in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi", "sqlalchemy"]:
        _logger = logging.getLogger(_log)
        _logger.handlers = [InterceptHandler()]

    logger.info(f"Logging initialized with level: {settings.LOG_LEVEL}")
