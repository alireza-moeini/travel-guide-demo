import asyncio
import json
import logging

from flask import Blueprint, request, jsonify, make_response
from ..controllers.flight import FlightController
from ..controllers.hotel import HotelController

flight_bp = Blueprint('flight', __name__)

flight_controller = FlightController()
hotel_controller = HotelController()


async def search_travels():
    logger = logging.getLogger("stream")

    query_params = request.args.to_dict()

    flights = await flight_controller.fetch_flight_offers(query_params)
    hotels = await hotel_controller.fetch_hotel_offers(query_params)
    result = {
        "flights": flights,
        "hotels": hotels
    }

    return make_response(jsonify(result), 200)
