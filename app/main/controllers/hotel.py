import asyncio
import itertools
import logging
from typing import List

import aiohttp
from aiohttp import ClientSession

from .base import BaseController
from .. import redis_cache, database
from .. import default_config
from ..utils.utils import remove_none_values, chunk_list


class HotelController(BaseController):
    def __init__(self):
        self.headers = {
            "Authorization": redis_cache.get("TOKEN").decode()
        }
        self.logger = logging.getLogger('stream')
        super().__init__(self.headers)

    async def fetch_hotels(self, session: aiohttp.ClientSession, params):
        result = await self.fetch_data(session, default_config['API_PROVIDER']['ENDPOINTS']['HOTEL']['SEARCH'],
                                       params=params)
        if result.get('errors', None) is not None:
            self.logger.error(f"API Error - Params: {params} - Result: {result}")

        return result

    async def search_hotels(self, params):
        cities = params.get("cities", None)
        if cities is None or not isinstance(cities, list) != "list" or len(cities) == 0:
            return {
                "message": "Required parameter 'cities' was not correctly provided",
                "code": 400
            }
        filters = {
            "iataCode": {"$in": cities}
        }
        if params.get("ratings", None) is not None:
            filters["rating"] = {"$in": params['ratings']}
        if params.get("name", None) is not None:
            filters["name"] = {'$regex': params.get("name"), '$options': 'i'}

        hotels = await database.find(default_config["DATABASE"]["COLLECTIONS"]["HOTEL"], filters)
        return hotels

    async def fetch_hotel_offers(self, params):
        dest = params.get("dest", None)
        adults = params.get("adults", '1')
        check_in_date = params.get("checkInDate", None)
        check_out_date = params.get("checkOutDate", None)
        room_quantity = params.get("roomQuantity", '1')
        price_range = params.get("hotelPriceRange", None)
        currency = params.get("currency", None)
        board_type = params.get("hotelBoardType", None)
        best_rate_only = params.get("hotelBestRateOnly", "true")

        if dest is None:
            return {
                "message": "Required parameter 'dest' was not correctly provided",
                "code": 400
            }

        adults = int(adults)
        room_quantity = int(room_quantity)

        city_hotels = await database.find(
            collection_name=default_config["DATABASE"]["COLLECTIONS"]["HOTEL"],
            filters={"iataCode": dest},
            projections={"hotelId": True}
        )
        hotel_ids = list(map(lambda hotel: hotel["hotelId"], city_hotels))
        if len(hotel_ids) == 0:
            return []

        params = {
            "adults": adults,
            "checkInDate": check_in_date,
            "checkOutDate": check_out_date,
            "roomQuantity": room_quantity,
            "priceRange": price_range,
            "currency": currency,
            "boardType": board_type,
            "bestRateOnly": best_rate_only
        }
        params = remove_none_values(params)
        hotel_offers = []
        tasks = []
        chunked_ids = chunk_list(hotel_ids, 10)
        async with ClientSession() as session:
            for chunk in chunked_ids:
                params["hotelIds"] = ",".join(chunk)
                tasks.append(asyncio.create_task(
                    self.fetch_data(session, default_config['API_PROVIDER']['ENDPOINTS']['HOTEL']['OFFER'],
                                    params=params)))
            hotel_offers = await asyncio.gather(*tasks)
            hotel_offers = [hotel_offer['data'] for hotel_offer in hotel_offers if
                            hotel_offer.get('data', None) is not None]
            hotel_offers = list(itertools.chain(*hotel_offers))
        return hotel_offers

    async def get_hotel_ratings(self, session: aiohttp.ClientSession, hotel_ids: List[str]):
        params = {
            "hotelIds": ','.join(hotel_ids)
        }
        result = await self.fetch_data(session, default_config['API_PROVIDER']['ENDPOINTS']['HOTEL']['RATING'],
                                       params=params)
        if result.get('errors', None) is not None:
            self.logger.error(f"API Error - Params: {params} - Result: {result}")

        return result
