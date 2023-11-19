import logging
from typing import List

import aiohttp
from aiohttp import ClientSession

from .base import BaseController
from .. import redis_cache
from .. import default_config
from ..utils.utils import remove_none_values


class FlightController(BaseController):
    def __init__(self):
        self.headers = {
            "Authorization": redis_cache.get("TOKEN").decode()
        }
        self.logger = logging.getLogger('stream')
        super().__init__(self.headers)

    async def fetch_flight_offers(self, params):
        origin = params.get("origin", None)
        dest = params.get("dest", None)
        departure_date = params.get("departureDate", None)
        return_date = params.get("returnDate", None)
        adults = params.get("adults", None)
        travel_class = params.get("class", None)
        non_stop = params.get("nonStop", None)
        max_price = params.get("maxPrice", None)

        if origin is None or dest is None or departure_date is None or adults is None:
            return {
                "message": "Required parameters were not correctly provided",
                "code": 400
            }
        if adults is not None:
            adults = int(adults)
        if max_price is not None:
            max_price = int(max_price)

        params = {
            "originLocationCode": origin,
            "destinationLocationCode": dest,
            "departureDate": departure_date,
            "returnDate": return_date,
            "adults": adults,
            "travelClass": travel_class,
            "nonStop": non_stop,
            "maxPrice": max_price,
        }

        flights = []
        params = remove_none_values(params)
        async with ClientSession() as session:
            flight_result = await self.fetch_data(session,
                                                  default_config['API_PROVIDER']['ENDPOINTS']['FLIGHT']['OFFER'],
                                                  params=params)
            if flight_result.get('errors', None) is not None:
                self.logger.error(f"API Error - Params: {params} - Result: {flight_result}")
            flights = flight_result["data"]

        return flights
