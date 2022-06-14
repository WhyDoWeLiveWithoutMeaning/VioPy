"""
MIT License

Copyright (c) 2022 Meaning

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import websockets
import httpx
import asyncio
import json

from datetime import datetime, timezone
from ratelimiter import RateLimiter
from terminaltables import AsciiTable
from itertools import zip_longest

from typing import (
    Coroutine,
    Union,
    List,
    Dict,
    Set
)

BASE_URI = "http://adv.vi-o.tech/api"
WS_URI = "ws://adv.vi-o.tech/ws"
RATE_LIMITER = RateLimiter(60, 60)

class ItemSummary:
    """Represents the instance of an item summary.

    Parameters
    ----------
        data: :class:`dict`
            The data of the summary.
    """

    def __init__(self, data: dict) -> None:
        self._buy_volume: int = data["buy"].get("Volume", 0)
        self._buy_price: int = data["buy"].get("Best", 0)
        self._sell_volume: int = data["sell"].get("Volume", 0)
        self._sell_price: int = data["sell"].get("Best", 0)

    def __repr__(self) -> str:
        return f"<{self.__class__}({self.buy_volume=},{self.buy_price=},{self.sell_volume=},{self.sell_price=})>"

    def __str__(self) -> str:
        return AsciiTable(self._ascii_table()).table

    def _ascii_table(self) -> list:
        return [
            ["", "Sell Volume", "Sell Price", "Buy Volume", "Buy Price", ""],
            ["", self.sell_volume, self.sell_price, self.buy_volume, self.buy_price, ""]
        ]

    @property
    def buy_volume(self) -> int:
        """:class:`int`: The buy volume of the item"""
        return self._buy_volume

    @property
    def sell_volume(self) -> int:
        """:class:`int`: The sell volume of the item"""
        return self._sell_volume

    @property
    def buy_price(self) -> float:
        """:class:`float`: The best buy price of the item"""
        return self._buy_price

    @property
    def sell_price(self) -> float:
        """:class:`float`: The best sell price of the item"""
        return self._sell_price



class Listing:
    """Represents the instance of a single listing

    Parameters
    ----------
        data: :class:`dict`
            The data of the listing
    """

    def __init__(self, data: dict) -> None:
        self._id: int = data["userID"]
        self._volume: int = data["amount"]
        self._price: int = data["price"]

    def __repr__(self) -> str:
        return f"<{self.__class__}({self.id=},{self.volume=},{self.price=})>"

    def to_list(self) -> List[int]:
        """List[:class:`int`] The data in a list format
        
        [id, volume, price]
        """
        return [self.id, self.volume, self.price]

    @property
    def id(self) -> int:
        """:class:`int` The Vendor ID of the listing"""
        return self._id

    @property
    def volume(self) -> int:
        """:class:`int` The amount of items in the listing"""
        return self._volume

    @property
    def price(self) -> int:
        """:class:`int` The price of each item in the listing"""
        return self._price


class ItemListings:
    """Represents the instance of the listings of an Item

    Parameters
    ----------
        data: :class:`dict`
            A dictionary of the listings of an Item
    """

    def __init__(self, data: dict) -> None:
        self._buy: List[Listing] = [Listing(i) for i in data["buy"]]
        self._sell: List[Listing] = [Listing(i) for i in data["sell"]]

    def __repr__(self) -> str:
        return f"<{self.__class__}({self.buy=},{self.sell=})>"

    def _ascii_table(self) -> list:
        return [["", "Sell Orders", "", "", "Buy Orders", ""]] + \
            [ i[0] + i[1]
            for i in zip_longest(
                [i.to_list() for i in self.buy],
                [i.to_list() for i in self.sell],
                fillvalue=["", "", ""]
            )
        ]

    @property
    def buy(self) -> List[Listing]:
        """List[:class:`Listing`]: The buy listings of the Item"""
        return self._buy

    @property
    def sell(self) -> List[Listing]:
        """List[:class:`Listing`]: The sell listings of the Item"""
        return self._sell
    

class ScanInfo:
    """Represents the information about a scan.

    Parameters
    ----------
        data: :class:`dict`
            A dictionary of the Scan Information.
    """

    def __init__(self, data: dict):
        self._unix: int = data["capturedTime"]
        self._datetime: datetime = datetime.strptime(data["datetimeSaved"]["$date"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

    def __repr__(self) -> str:
        return f"<{self.__class__}({self._unix=},{self._datetime=})>"

    @property
    def unix(self) -> int:
        """:class:`int`: The UNIX timestamp of the scan."""
        return self._unix

    @property
    def unix_datetime(self) -> datetime:
        """:class:`datetime`: The datetime of the scan created from the UNIX timestamp."""
        return datetime.fromtimestamp(self.unix, timezone.utc)

    @property
    def datetime(self) -> datetime:
        """:class:`datetime`: The datetime of the scan."""
        return self._datetime

class ItemInstance:
    """Represents the instance of an item.

    Parameters
    ----------
        data: :class:`dict`
            the dictionary representing the item instance.

        item: :class:`str`
            the name of the item.

        scan_info: :class:`ScanInfo`
            the scan information.
    """

    def __init__(self, data: dict, item: str, scan_info: ScanInfo) -> None:
        self._item: str = item
        self._scan_info: ScanInfo = scan_info
        self._listings: ItemListings = ItemListings(data["listings"])
        self._summary: ItemSummary = ItemSummary(data["summary"])

    def __repr__(self) -> str:
        return f"<{self.__class__}({self.item=},{self.listings=},{self.summary=})>"

    def __str__(self) -> str:
        table = self.summary._ascii_table() + self.listings._ascii_table()
        str_tab = AsciiTable(table, title=self.item).table.split("\n")
        str_tab.insert(4, str_tab[2])
        str_tab.insert(6, str_tab[2])
        return "\n".join(str_tab)

    @property
    def item(self) -> str:
        """:class:`str`: The name of the item"""
        return self._item

    @property
    def scan_info(self) -> ScanInfo:
        """:class:`ScanInfo`: The scan information"""
        return self._scan_info

    @property
    def listings(self) -> ItemListings:
        """:class:`ItemListings`: The listings of the item"""
        return self._listings

    @property
    def summary(self) -> ItemSummary:
        """:class:`ItemSummary`: The summary of the item"""
        return self._summary
        

class MarketInstance:
    """Represents one instance of the market

    Parameters:
        data: :class:`dict`
            The data of the market.

    """

    def __init__(self, data: dict) -> None:
        self._id: int = data["_id"]
        self._scan_info: ScanInfo = ScanInfo(data["data"]["scInfo"])
        self._items: Dict[str, ItemInstance] = {k: ItemInstance(v, k, self.scan_info) for k, v in data["data"]["marketInfo"].items()}

    def __repr__(self) -> str:
        return f"<{self.__class__}({self.id=},{self.scan_info=},{self.items=})>"
    
    def __getitem__(self, item: str) -> Union[ItemInstance, None]:
        return self.items.get(item, None)

    @property
    def id(self) -> int:
        """:class:`int`: The id of the market"""
        return self._id

    @property
    def scan_info(self) -> ScanInfo:
        """:class:`ScanInfo`: The scan information of the market"""
        return self._scan_info

    @property
    def items(self) -> Dict[str, ItemInstance]:
        """Dict[:class:`str`, :class:`ItemInstance`]: The items of the market"""
        return self._items

class Vio:
    """ Represents an instance of the vio API, with a certain key.

    Parameters
    ----------
        key: :class:`str`
            The key of the vio API.
    """

    def __init__(self, key: str) -> None:
        self.key = key
        
        self._headers = {
            "X-API-KEY": self.key,
        }
        
        self._cached_market: Set[MarketInstance] = set()

    def current(self) -> MarketInstance: 
        """Get the current market

        :return: The current market.
        """

        with RATE_LIMITER:
            res = httpx.get(
                f"{BASE_URI}/market",
                headers=self._headers
                ).json()

            self._latest_market = MarketInstance(res)
            if self._latest_market not in self._cached_market:
                self._cached_market.add(self._latest_market)

            return self._latest_market

    def market_scan(self, id: int) -> MarketInstance:
        """Get a market scan from a previous date.

        Returns
        -------
            :class:`MarketInstance`
        """

        with RATE_LIMITER:
            res = httpx.get(
                f"{BASE_URI}/market/{id}",
                headers=self._headers
                ).json()

            market = MarketInstance(res)

            if market not in self._cached_market:
                self._cached_market.add(market)

            return market

    def scan_history(self) -> Dict[datetime, int]:
        """Get a dictionary of Datetimes to ints of the scan history.

        Returns
        -------
            Dict[:class:`datetime`, :class:`int`]
        :return: A dictionary of Datetimes to ints of the scan history.
        """

        with RATE_LIMITER:
            res = httpx.get(
                f"{BASE_URI}/market/history",
                headers=self._headers
                ).json()

            return {datetime.fromisoformat(k): v for k, v in res.items()}
        

    def item_history(self, item:str) -> List[ItemInstance]:
        """Get the entire scan history of an Item

        :param item: The item to get the history of.
        :return: The history of the item.
        """

        with RATE_LIMITER:
            res = httpx.get(
                f"{BASE_URI}/item/{item}/all",
                headers=self._headers
                )

            return [
                ItemInstance(i["data"]["marketInfo"][item], item, ScanInfo(i["data"]["scInfo"])) 
                for i in res.json()
            ]

class AsyncVio:
    """AsyncVio Class

    Represents an Asynchronous instance of the vio API, with a certain key.

    Parameters
    ----------
        key: :class:`str` 
            The API key to use.
    """

    
    def __init__(self, key: str) -> None:
        self.key = key
        self._headers = {
            "X-API-KEY": self.key,
        }

        self._cached_market: Set[MarketInstance] = set()

        self._listening: asyncio.Lock = asyncio.Lock()
        self._coro_list: Set[Coroutine] = set()

    ## MARKET

    async def current(self) -> MarketInstance:
        """Get the current market

        Returns
        -------
            :class:`MarketInstance`
        """

        async with RATE_LIMITER:
            async with httpx.AsyncClient() as client:
                res = await client.get(
                    f"{BASE_URI}/market",
                    headers=self._headers
                    )

            self._latest_market = MarketInstance(res.json())
            if self._latest_market not in self._cached_market:
                self._cached_market.add(self._latest_market)
            return self._latest_market

    async def market_scan(self, id: int) -> MarketInstance:
        """Get a market scan from a previous date.

        Returns
        -------
            :class:`MarketInstance`
        """

        async with RATE_LIMITER:
            async with httpx.AsyncClient() as client:
                res = await client.get(
                    f"{BASE_URI}/market/{id}",
                    headers=self._headers
                    )

            market = MarketInstance(res.json())

            if market not in self._cached_market:
                self._cached_market.add(market)

            return market

    async def scan_history(self) -> Dict[datetime, int]:
        """Get a dictionary of Datetimes to ints of the scan history.

        Returns
        -------
            Dict[:class:`datetime`, :class:`int`]
        :return: A dictionary of Datetimes to ints of the scan history.
        """
        async with RATE_LIMITER:
            async with httpx.AsyncClient() as client:
                res = await client.get(
                    f"{BASE_URI}/market/history",
                    headers=self._headers
                    )

            return {datetime.fromisoformat(k): v for k, v in res.items()}

    ## ITEMS

    async def item_history(self, item: str) -> List[ItemInstance]:
        """Get the entire scan history of an Item

        Parameters
        ----------
            item: :class:`str`
                The item to get the history of.
        Returns
        -------
            :class:`List[ItemInstance]`
        """
        async with RATE_LIMITER:
            async with httpx.AsyncClient() as client:
                res = await client.get(
                    f"{BASE_URI}/item/{item}/all",
                    headers=self._headers
                    )

            return [
                ItemInstance(i["data"]["marketInfo"][item], item, ScanInfo(i["data"]["scInfo"])) 
                for i in res.json()
            ]

    ## WS

    async def listen(self) -> None:
        """
        Creates a websocket connection and lets the websocket listen to 
        messages from VIO. This will run forever.

        """
        if self._listening.locked():
            return

        async with self._listening:
            async for socket in websockets.connect(WS_URI, extra_headers=self._headers):
                try:
                    while True:
                        res = await socket.recv()
                        res = json.loads(res)
                        if res["Rtype"] == "Update":
                            instance = MarketInstance(res["DataType"])
                            self._cached_market.add(instance)
                            await asyncio.gather(*[coro(instance) for coro in self._coro_list])
                except websockets.ConnectionClosed:
                    pass

    def run(self) -> None:
        """A blocking call that runs the listen coroutine.
        
        If you want more control then use :meth:`listen` instead.
        """
        try:
            asyncio.run(self.listen())
        except KeyboardInterrupt:
            pass
        
    def event(self, coro: Coroutine) -> Coroutine:
        """A decorator that registers a coroutine to be called when new market data is received.
        
        Example
        -------

        .. code-block:: python3

            @vio.event
            async def print_market(market: MarketInstance):
                print(market["Korrelite"])
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("event must be a coroutine function")

        self._coro_list.add(coro)
        return coro
        
        
        
