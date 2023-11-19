import logging
from logging import config
from .utils import ROOT_DIR
import os


def init_logger():
    log_path = os.path.join(ROOT_DIR, "logs")
    config_path = os.path.join(ROOT_DIR, "configs")
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    config.fileConfig(os.path.join(os.path.join(config_path, "logger.ini")),
                      defaults={'log_filename': os.path.join(log_path, 'app.log')})
