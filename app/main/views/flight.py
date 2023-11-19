import asyncio
import json
import logging

from flask import Blueprint, request, jsonify, make_response
from ..controllers.flight import FlightController


flight_bp = Blueprint('flight', __name__)

flight_controller = FlightController()


async def search_flights():
    logger = logging.getLogger("stream")

    query_params = request.args.to_dict()

    flights = await flight_controller.fetch_flight_offers(query_params)

    return make_response(jsonify(flights), 200)
