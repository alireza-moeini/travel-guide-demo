import asyncio
import json
import logging

from aiohttp import ClientSession
from flask import Blueprint, request, jsonify, make_response
import itertools
from ..controllers.hotel import HotelController
from ..controllers.geo import GeoController
from ..utils.utils import chunk_list, remove_none_values, strtobool
from .. import database, default_config

hotel_bp = Blueprint('hotel', __name__)

hotel_controller = HotelController()
geo_controller = GeoController()


async def get_hotels():
    logger = logging.getLogger("stream")

    query_params = request.args.to_dict()
    logger.info(query_params)

    limit = query_params.get("limit", None)
    offset = query_params.get("offset", None)
    if limit is not None:
        limit = int(limit)
    if offset is not None:
        offset = int(offset)
    hotels = await database.find(default_config["DATABASE"]["COLLECTIONS"]["HOTEL"], limit=limit, offset=offset)
    return make_response(jsonify(hotels), 200)


async def get_hotel(hotel_id):
    """
    Asynchronously retrieve the list of hotels.
    Allow for concurrent execution of API calls
    """
    if not hotel_id:
        return make_response(jsonify({
            "message": "Required path parameter 'hotel_id' not provided.",
            "code": 400
        }))
    filters = {
        "hotelId": hotel_id
    }
    hotel = await database.find_one(default_config["DATABASE"]["COLLECTIONS"]["HOTEL"], filters)
    if not hotel:
        return make_response(jsonify({
            "message": "Hotel not found",
            "code": 404
        }))
    return make_response(jsonify(hotel), 200)


async def search_hotels():
    request_params = request.args.to_dict()
    logger = logging.getLogger("stream")
    logger.info(request_params)
    cities = request_params.get("cities", "")
    ratings = request_params.get("ratings", "")

    cities = cities.split(",")
    ratings = list(map(lambda item: int(item), ratings.split(",")))

    params = {
        "cities": cities,
        "ratings": ratings,
        "name": request_params.get("name", None)
    }

    hotels = await hotel_controller.search_hotels(params)

    return make_response(jsonify(hotels), 200)


async def find_hotels():
    """
    Asynchronously retrieve the list of hotels.
    Allow for concurrent execution of API calls
    """
    request_body = request.get_json()

    hotels = await hotel_controller.search_hotels(request_body)

    return make_response(jsonify(hotels), 200)


async def get_hotel_offers():
    logger = logging.getLogger("stream")

    query_params = request.args.to_dict()

    hotel_offers, code = await hotel_controller.fetch_hotel_offers(query_params)

    return make_response(jsonify(hotel_offers), code)


async def get_hotel_rating():
    """
    Asynchronously retrieve the ratings of hotels.
    """
    data = request.json
    hotel_ids = data["hotelIds"]
    chunked_hotel_ids = chunk_list(hotel_ids, 3)
    async with ClientSession() as session:
        tasks = []
        for chunked_ids in chunked_hotel_ids:
            tasks.append(asyncio.create_task(hotel_controller.get_hotel_ratings(session, chunked_ids)))
        ratings = await asyncio.gather(*tasks)
        ratings = list(map(lambda ratings_info: ratings_info['data'], ratings))
        ratings = list(itertools.chain(*ratings))
        return ratings
