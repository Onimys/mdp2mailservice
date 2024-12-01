import logging
import logging.config
from functools import lru_cache
from pathlib import Path

import structlog
from structlog.typing import EventDict, Processor

from mdp2mailservice.common.constants import Environment

from .config import settings

__all__ = ["configure_logger", "get_logger"]

DEFAULT_LOGGER_NAME = settings.APP_NAME


def rename_event_key(_: logging.Logger, __: str, event_dict: EventDict) -> EventDict:
    """
    Rename `event` field to `message`.
    """
    event_dict["message"] = event_dict.pop("event")
    return event_dict


def drop_color_message_key(_: logging.Logger, __: str, event_dict: EventDict) -> EventDict:
    """
    Uvicorn logs the message a second time in the extra `color_message`, but we don't
    need it.
    This processor drops the key from the event dict if it exists.
    """
    event_dict.pop("color_message", None)
    return event_dict


def extract_from_record(_: logging.Logger, __: str, event_dict: EventDict):
    """
    Extract thread and process names and add them to the event dict.
    """
    record = event_dict["_record"]
    event_dict["thread_name"] = record.threadName
    event_dict["process_name"] = record.processName
    return event_dict


def configure_logger(json_logs: bool = False) -> None:
    timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")

    pre_chain = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.ExtraAdder(),
        timestamper,
    ]

    if settings.ENVIRONMENT == Environment.PRODUCTION:
        if not Path(settings.LOGS_FOLDER).is_dir():
            Path(settings.LOGS_FOLDER).mkdir(parents=True)

        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "plain": {
                        "()": structlog.stdlib.ProcessorFormatter,
                        "processors": [
                            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                            structlog.dev.ConsoleRenderer(colors=False),
                        ],
                        "foreign_pre_chain": pre_chain,
                    },
                },
                "handlers": {
                    "file": {
                        "level": settings.LOG_LEVEL,
                        "class": "logging.handlers.RotatingFileHandler",
                        "formatter": "plain",
                        "filename": f"{settings.LOGS_FOLDER}/app.log",
                        "maxBytes": 10000,
                        "backupCount": 10,
                    },
                },
                "loggers": {
                    "": {
                        "handlers": ["file"],
                        "level": settings.LOG_LEVEL,
                        "propagate": True,
                    },
                },
            }
        )

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        drop_color_message_key,
        timestamper,
        structlog.processors.StackInfoRenderer(),
    ]

    if json_logs:
        shared_processors.append(rename_event_key)
        shared_processors.append(structlog.processors.format_exc_info)

    structlog.configure(
        processors=shared_processors + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    log_renderer = structlog.processors.JSONRenderer() if json_logs else structlog.dev.ConsoleRenderer()

    _configure_default_logging_by_custom(shared_processors, log_renderer)


def _configure_default_logging_by_custom(
    shared_processors: list[Processor], log_renderer: structlog.types.Processor
) -> None:
    # Use `ProcessorFormatter` to format all `logging` entries.
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            # Remove _record & _from_structlog.
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            log_renderer,
        ],
    )

    handler = logging.StreamHandler()
    # Use structlog `ProcessorFormatter` to format all `logging` entries.
    handler.setFormatter(formatter)

    # Disable the `passlib` logger.
    logging.getLogger("passlib").setLevel(logging.ERROR)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    # Set logging level.
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(settings.LOG_LEVEL)

    for _log in [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "faststream",
        "faststream.access",
        "faststream.error",
        "faststream.access.rabbit",
    ]:
        logging.getLogger(_log).handlers.clear()
        logging.getLogger(_log).propagate = True


@lru_cache
def get_logger(file_name: str) -> structlog.stdlib.BoundLogger:
    logger = structlog.get_logger()
    logger.bind(file_name=file_name)
    return logger
