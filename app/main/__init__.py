import logging
import os
import sys

import requests

from .utils import default_config, database, redis_cache
from .utils import init_logger


def authenticate():
    logger = logging.getLogger("stream")
    try:
        auth_url = default_config["API_PROVIDER"]["ENDPOINTS"]["AUTH"]
        data = {
            'grant_type': "client_credentials",
            'client_id': default_config["API_PROVIDER"]["CRED"]["KEY"],
            'client_secret': default_config["API_PROVIDER"]["CRED"]["SECRET"],
        }
        response = requests.post(url=auth_url, data=data)
        logger.info(response)
        response_json = response.json()
        logger.info(f"Bearer {response_json['access_token']}")
        redis_cache.set("TOKEN", f"Bearer {response_json['access_token']}")
    except Exception as error:
        logger.error(f"Authentication failed = {error}")

def ensure_database_populate():
    database.ensure_collection_exists(default_config["DATABASE"]["COLLECTIONS"]["HOTEL"])
    database.ensure_collection_exists(default_config["DATABASE"]["COLLECTIONS"]["FLIGHT"])
    from .views.hotel import search_hotels


def init_db():
    database.init_db()


def bootstrap():
    logger = None
    try:
        init_logger()
        logger = logging.getLogger("root")
        init_db()
        authenticate()

    except Exception as error:
        logger.info(f"Bootstrap failed - {str(error)}")
        sys.exit(1)
