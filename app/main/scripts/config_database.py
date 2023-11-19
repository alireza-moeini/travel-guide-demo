import asyncio

import pymongo
from pymongo.collation import Collation

from .. import bootstrap, database, default_config


async def configure_collections():
    hotel_collection = database.get_collection(default_config["DATABASE"]["COLLECTIONS"]["HOTEL"])
    await hotel_collection.create_index([('name', pymongo.TEXT)], name='name_index')


if __name__ == '__main__':
    bootstrap()
    asyncio.run(configure_collections())
