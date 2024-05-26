
import logging
from logging.config import dictConfig

config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"default": {"format": "%(asctime)s | %(levelname)s | %(message)s"}},
    "handlers": {
        "errors": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": "errors.log",
        },
        "info": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": "info.log",
        },
    },
    "loggers": {
        "errors": {"level": logging.ERROR, "handlers": ["errors"]},
        "info": {"level": logging.INFO, "handlers": ["info"]},
    },
}

dictConfig(config)

errors = logging.getLogger("errors")
info = logging.getLogger("info")