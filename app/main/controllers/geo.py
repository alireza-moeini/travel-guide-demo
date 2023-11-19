import asyncio
import json
import logging
from typing import List, Dict, Any

import aiohttp
from .base import BaseController
from .. import default_config

GEO_CODE_BATCH = []
GEO_BATCH_LOOP_RUNNING = False


class GeoController(BaseController):

    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.params = {
            "apiKey": default_config["API_PROVIDER"]["CRED"]["API_KEY"]
        }
        super().__init__(self.headers, self.params)

    def __merge_data(self, params):
        return self.headers | params

    async def reverse_geocode(self, session: aiohttp.ClientSession, geo_codes):
        # Make the POST request to the API
        url = default_config['API_PROVIDER']['ENDPOINTS']['GEO']['REVERSE']

        async with session.post(url, headers=self.headers, data=json.dumps(geo_codes), params=self.params,
                                ssl=False) as response:
            response_json = await response.read()
            response_data = json.loads(response_json)

        # The API can return a dict with a pending status if it needs more
        # time to complete. Poll the API until the result is ready.
        logger = logging.getLogger("stream")

        attempts = 50
        while isinstance(response_data, dict) \
                and response_data.get("status") == "pending":
            # Query the result to see if it's ready yet
            request_id = response_data.get("id")
            updated_params = self.params.copy()
            updated_params['id'] = request_id

            async with session.get(url, params=updated_params, ssl=False) as response:
                response_json = await response.read()
                response_data = json.loads(response_json)
            attempts -= 1
            if attempts <= 0:
                break
        if isinstance(response_data, dict) and (
                response_data.get("status") == "not found" or response_data.get("status") == "pending"):
            return {}
        # Gather the results into a dictionary of address -> (lat, lon)
        locations = {}
        for result in response_data:
            coords = str(result["query"]["lat"]), str(result["query"]["lon"])
            locations['_'.join(coords)] = {
                "country_code": result.get("country_code", None),
                "housenumber": result.get("housenumber", None),
                "street": result.get("street", None),
                "country": result.get("country", None),
                "county": result.get("county", None),
                "district": result.get("district", None),
                "city": result.get("city", None),
                "address_line1": result.get("address_line1", None),
                "address_line2": result.get("address_line2", None)
            }
        return locations
