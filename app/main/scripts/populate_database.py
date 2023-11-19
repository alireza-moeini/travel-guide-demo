import asyncio
import itertools

from aiohttp import ClientSession

from ..controllers.geo import GeoController
from ..utils.utils import chunk_list
from ..utils.config_parser import parse_config
from ..controllers.hotel import HotelController
from .. import bootstrap, database, default_config
import logging
from random import randint

hotel_controller = HotelController()
geo_controller = GeoController()


async def populate_database():
    hotels = await fetch_hotel_info()
    # hotels = await database.find(default_config["DATABASE"]["COLLECTIONS"]["HOTEL"], {})
    # hotel_ids = list(map(lambda item: item["hotelId"], hotels))
    # ratings = await fetch_hotel_ratings(hotel_ids)
    rated_hotels = await assign_ratings(hotels)
    await database.bulk_save(rated_hotels, default_config["DATABASE"]["COLLECTIONS"]["HOTEL"])
    # await database.bulk_save(ratings, default_config["DATABASE"]["COLLECTIONS"]["RATING"])


async def fetch_hotel_info():
    logger = logging.getLogger("stream")
    iata_info = parse_config("iata_codes.json")
    city_codes = iata_info["CITY_CODES"]
    logger.debug(", ".join(city_codes))

    hotels = []
    async with ClientSession() as session:
        tasks = []
        for code in city_codes:
            query_params = {
                "cityCode": code
            }
            task = asyncio.create_task(hotel_controller.fetch_hotels(session, query_params))
            tasks.append(task)
        hotels = await asyncio.gather(*tasks)

    hotels = list(map(lambda city_result: city_result['data'], hotels))
    # Flatten the results
    hotels = list(itertools.chain(*hotels))
    hotels_geo_info = list(map(lambda hotel: {'id': hotel['hotelId'], 'lat': hotel['geoCode']['latitude'],
                                              'lon': hotel['geoCode']['longitude']}, hotels))
    async with ClientSession() as session:
        chunked_hotels_info = chunk_list(hotels_geo_info, 20)
        geo_tasks = []
        for chunk in chunked_hotels_info:
            geo_task = asyncio.create_task(geo_controller.reverse_geocode(session, chunk))
            geo_tasks.append(geo_task)
        locations = await asyncio.gather(*geo_tasks)

    locations_combined = {}
    for locations_info in locations:
        locations_combined.update(locations_info)
    for hotel in hotels:
        hotel["address"] = locations_combined.get(f"{hotel['geoCode']['latitude']}_{hotel['geoCode']['longitude']}",
                                                  None)
    return hotels


async def fetch_hotel_ratings(hotel_ids):
    """
    Asynchronously retrieve the ratings of hotels.
    """
    chunked_hotel_ids = chunk_list(hotel_ids, 3)
    async with ClientSession() as session:
        tasks = []
        ratings = []
        for chunked_ids in chunked_hotel_ids:
            tasks.append(asyncio.create_task(hotel_controller.get_hotel_ratings(session, chunked_ids)))
            ratings.extend(await asyncio.gather(*tasks))
            tasks = list()
            await asyncio.sleep(0.2)
        ratings = [rating_info['data'] for rating_info in ratings if rating_info.get('data', None) is not None]
        ratings = list(itertools.chain(*ratings))
        return ratings


async def assign_rating(hotels):
    for hotel in hotels:
        hotel['rating'] = randint(1, 5)
    return hotels


async def assign_ratings(hotels):
    chunked_hotels = chunk_list(hotels, 100)
    tasks = []
    for chunk in chunked_hotels:
        tasks.append(asyncio.create_task(assign_rating(chunk)))
    rated_hotels = await asyncio.gather(*tasks)
    rated_hotels = list(itertools.chain(*rated_hotels))
    return rated_hotels


if __name__ == '__main__':
    bootstrap()
    """
    loop = asyncio.new_event_loop()
    loop.run_until_complete(populate_database())
    """
    asyncio.run(populate_database())
