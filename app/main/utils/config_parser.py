import configparser
import json

from .utils import ROOT_DIR
import os


def parse_config(filename):
    ext = filename.split(".")[1]
    filepath = os.path.join(ROOT_DIR, "configs", filename)
    if ext == 'ini':
        config = configparser.ConfigParser()
        config.read(filepath)
        return config
    else:
        config = open(filepath, mode='r')
        return json.load(config)
