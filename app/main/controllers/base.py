import aiohttp
from aiohttp import ClientSession
from abc import ABC, abstractmethod


class BaseController(ABC):
    def __init__(self, headers, params=None):
        if params is None:
            params = {}
        self.headers = headers
        self.params = params
        super().__init__()

    async def fetch_data(self, session: ClientSession, url: str, headers=None, params=None):
        if headers is None:
            headers = self.headers

        async with session.get(
                url=url,
                headers=headers,
                params=params
        ) as response:
            return await response.json()

    async def post(self, session: ClientSession, url: str, headers=None, params=None, data=None):
        if headers is None:
            headers = self.headers

        async with session.post(
                url=url,
                headers=headers,
                params=params,
                data=data
        ) as response:
            return await response.json()
