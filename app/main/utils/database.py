import asyncio
import logging
import sys
from datetime import datetime
from typing import List
from pymongo import UpdateOne, InsertOne
from motor.motor_asyncio import AsyncIOMotorClient
import logging

from pymongo.collation import Collation

from .utils import chunk_list


class DatabaseUtils:
    def __init__(self, uri=None, db_name=None, connection_args=None):
        self.logger = logging.getLogger("general")
        self.client: AsyncIOMotorClient = None
        self.db_name = db_name
        self.uri = uri
        self.connection_args = connection_args
        self.db = None
        self.__batch_size = 500

    def init_db(self):
        try:
            self.client = AsyncIOMotorClient(self.uri, **self.connection_args)
            self.client.get_io_loop = asyncio.get_event_loop
            self.db = self.client.get_database(self.db_name)
            self.logger.info("Successfully established connection to database")
        except Exception as error:
            self.logger.critical(f"Could not connect to database - {str(error)}")
            sys.exit(1)

    async def ping_server(self):
        try:
            self.client.admin.command('ping')
            self.logger.info("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as error:
            self.logger.critical(f"Could not connect to database - {str(error)}")

    def ensure_collection_exists(self, collection):
        try:
            new_collection = self.db[collection]
        except Exception as error:
            self.logger.error(f"Could not create new collection - {str(error)}")

    def get_collection(self, collection):
        try:
            return self.db.get_collection(collection)
        except Exception as error:
            self.logger.error(f"Could not get collection - {str(error)}")

    async def bulk_save(self, data: List[any], collection_name):
        self.ensure_collection_exists(collection_name)
        collection = self.db.get_collection(collection_name)
        operations = list(map(lambda item: InsertOne(item), data))

        chunked_data = chunk_list(operations, self.__batch_size)
        for chunk in chunked_data:
            collection.bulk_write(chunk, ordered=False)

    async def find(self, collection_name, filters=None, projections=None, limit=0, offset=0):
        if filters is None:
            filters = {}
        collection = self.db.get_collection(collection_name)
        if projections is None:
            projections = {}

        projections["_id"] = False

        cursor = collection \
            .find(filter=filters, projection=projections, limit=limit) \
            .skip(offset) \
            .limit(limit) \
            .collation(Collation(locale='en_US', strength=2))

        # it gets interesting here now. Iterate over the cursor asynchronously
        result = [item async for item in cursor]
        return result

    async def find_one(self, collection_name, filters):
        collection = self.db.get_collection(collection_name)

        projection = {
            "_id": False
        }
        result = await collection.find_one(filter=filters, projection=projection)

        return result
