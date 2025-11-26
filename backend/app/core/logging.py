import logging
import sys
from typing import Any

from ..config import settings

class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/health") == -1

def setup_logging() -> None:
    """
    Configure the logging system.
    """
    # Set default log level based on DEBUG setting
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # Create formatter
    # Format: [Time] [Level] [Module:Line] Message
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    # Add filter to remove health check noise if needed
    # handler.addFilter(EndpointFilter())

    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    logger.addHandler(handler)

    # Set log levels for specific libraries to reduce noise
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)

    # If specific logger needed for app
    app_logger = logging.getLogger("app")
    app_logger.setLevel(log_level)
