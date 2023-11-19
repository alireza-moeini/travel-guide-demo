import logging
from pathlib import Path

from .config_parser import parse_config
from .redis import setup_redis
from .database import DatabaseUtils
from .logger import init_logger

default_config = parse_config("default.json")
redis_cache = setup_redis()
database = DatabaseUtils(default_config["DATABASE"]["URI"], default_config["DATABASE"]["NAME"],
                         default_config["DATABASE"]["CONNECTION_ARGS"])
