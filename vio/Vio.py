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


def _get_ids_from_market(data: dict) -> List[int]:
    ids = []
    for i in data["data"]["marketInfo"].values():
        for j in i["listings"].values():
            for k in j:
                if k["userID"] not in ids:
                    ids.append(k["userID"])
    return ids


class RobloxUser:
    """Represents a Roblox user.

    Parameters
    ----------
        data: :class:`dict`
            The user data.
    """

    def __init__(self, data: dict) -> None:
        self._id = data["_id"]
        self._name = data["name"]
        self._display_name = data["displayName"]
        self._url = data["roblox_profile"]
        self._tiny_url = data["roblox_tiny_profile"]

    @property
    def id(self) -> int:
        """:class:`int` The user's ID."""
        return self._id

    @property
    def name(self) -> str:
        """:class:`str` The user's name."""
        return self._name

    @property
    def display_name(self) -> str:
        """:class:`str` The user's display name."""
        return self._display_name

    @property
    def url(self) -> str:
        """:class:`str` The user's URL."""
        return self._url

    @property
    def tiny_url(self) -> str:
        """:class:`str` The user's tiny URL."""
        return self._tiny_url



class ItemSummary:
    """Represents the instance of an item summary.

    Parameters
    ----------
        data: :class:`dict`
            The data of the summary.
    """

    def __init__(self, data: dict, *args, **kwargs) -> None:
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

    def __init__(self, data: dict, *args, **kwargs) -> None:
        self._id: int = data["userID"]
        self._user: Union[RobloxUser, None] = next(iter([i for i in kwargs.get("users", None) if i.id == self._id]), None) if kwargs.get("users", None) else None
        self._volume: int = data["amount"]
        self._price: int = data["price"]

    def __repr__(self) -> str:
        return f"<{self.__class__}({self.id=},{self.volume=},{self.price=})>"

    def to_list(self, has_user = False) -> List[int]:
        """List[:class:`int`] The data in a list format
        
        [id, volume, price]
        """
        return [self.user.name, self.volume, self.price] if has_user else [self.id, self.volume, self.price]

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

    @property
    def user(self) -> Union[RobloxUser, None]:
        """:class:`RobloxUser` The user of the listing
        
        If the user is not found, this will be None."""
        return self._user


class ItemListings:
    """Represents the instance of the listings of an Item

    Parameters
    ----------
        data: :class:`dict`
            A dictionary of the listings of an Item
    """

    def __init__(self, data: dict, *args, **kwargs) -> None:
        self._buy: List[Listing] = [Listing(i, *args, **kwargs) for i in data["buy"]]
        self._sell: List[Listing] = [Listing(i, *args, **kwargs) for i in data["sell"]]

    def __repr__(self) -> str:
        return f"<{self.__class__}({self.buy=},{self.sell=})>"

    def _ascii_table(self, has_users = False) -> list:
        return [["", "Sell Orders", "", "", "Buy Orders", ""]] + \
            [ i[0] + i[1]
            for i in zip_longest(
                [i.to_list(has_users) for i in self.buy],
                [i.to_list(has_users) for i in self.sell],
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

    def __init__(self, data: dict, *args, **kwargs):
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

    def __init__(self, data: dict, item: str, scan_info: ScanInfo, *args, **kwargs) -> None:
        self._item: str = item
        self._scan_info: ScanInfo = scan_info
        self._listings: ItemListings = ItemListings(data["listings"], *args, **kwargs)
        self._summary: ItemSummary = ItemSummary(data["summary"], *args, **kwargs)
        self._has_users = True if kwargs.get("users", None) else False

    def __repr__(self) -> str:
        return f"<{self.__class__}({self.item=},{self.listings=},{self.summary=})>"

    def __str__(self) -> str:
        table = self.summary._ascii_table() + self.listings._ascii_table(self._has_users)
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

    Parameters
    -----------
        data: :class:`dict`
            The data of the market.
    """

    def __init__(self, data: dict, *args, **kwargs) -> None:
        self._id: int = data["_id"]
        self._scan_info: ScanInfo = ScanInfo(data["data"]["scInfo"], *args, **kwargs)
        self._items: Dict[str, ItemInstance] = {k: ItemInstance(v, k, self.scan_info, *args, **kwargs) for k, v in data["data"]["marketInfo"].items()}

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

    def current(self, *args, **kwargs) -> MarketInstance: 
        """Get the current market

        :return: The current market.
        """
        res = httpx.get(
            f"{BASE_URI}/market",
            headers=self._headers
            ).json()

        if kwargs.get("query_users", True):
            ids = _get_ids_from_market(res)
            all_users = self.get_users(ids)
            kwargs["users"] = all_users

        self._latest_market = MarketInstance(res, *args, **kwargs)
        if self._latest_market not in self._cached_market:
            self._cached_market.add(self._latest_market)

        return self._latest_market

    def market_scan(self, id: int, *args, **kwargs) -> MarketInstance:
        """Get a market scan from a previous date.

        Returns
        -------
            :class:`MarketInstance`
        """

        res = httpx.get(
            f"{BASE_URI}/market/{id}",
            headers=self._headers
            ).json()

        if kwargs.get("query_users", True):
            ids = _get_ids_from_market(res)
            all_users = self.get_users(ids)
            kwargs["users"] = all_users

        market = MarketInstance(res, *args, **kwargs)

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
        res = httpx.get(
            f"{BASE_URI}/market/history",
            headers=self._headers
            ).json()

        return {datetime.fromisoformat(k): v for k, v in res.items()}

    def all_items(self) -> List[str]:
        """Get a list of every item.

        Returns
        -------
            List[:class:`str`]
        :return: A list of every item.
        """
        res = httpx.get(
            f"{BASE_URI}/items",
            headers=self._headers
            ).json()

        return res 

    def item_history(self, item:str) -> List[ItemInstance]:
        """Get the entire scan history of an Item

        :param item: The item to get the history of.
        :return: The history of the item.
        """
        res = httpx.get(
            f"{BASE_URI}/item/{item}/all",
            headers=self._headers
            )

        return [
            ItemInstance(i["data"]["marketInfo"][item], item, ScanInfo(i["data"]["scInfo"])) 
            for i in res.json()
        ]

    def get_users(self, ids: List[int]) -> List[RobloxUser]:
        """Get a list of roblox users from vendor id's.

        Parameters
        ----------
            ids: :class:`List[int]`
                The vendor id's of the users to get.

        Returns
        -------
            :class:`List[User]`
        """
        res = httpx.post(
            f"{BASE_URI}/roblox",
            headers=self._headers,
            json=ids
            ).json()

        return [RobloxUser(u) for u in res]

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

    async def current(self, *args, **kwargs) -> MarketInstance:
        """Get the current market

        Parameters
        ----------
            query_users: :class:`bool`
                Whether or not to query the users of the listings.

        Returns
        -------
            :class:`MarketInstance`
        """
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{BASE_URI}/market",
                headers=self._headers
                )

        if kwargs.get("query_users", True):
            ids = _get_ids_from_market(res)
            all_users = await self.get_users(ids)
            kwargs["users"] = all_users

        self._latest_market = MarketInstance(res.json(), *args, **kwargs)
        if self._latest_market not in self._cached_market:
            self._cached_market.add(self._latest_market)
        return self._latest_market

    async def market_scan(self, id: int, *args, **kwargs) -> MarketInstance:
        """Get a market scan from a previous date.

        Parameters
        ----------
            id: :class:`int`
                The id of the market scan to get.

            query_users: :class:`bool`
                Whether or not to query the users of the listings.

        Returns
        -------
            :class:`MarketInstance`
        """

        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{BASE_URI}/market/{id}",
                headers=self._headers
                )

        if kwargs.get("query_users", True):
            ids = _get_ids_from_market(res)
            all_users = await self.get_users(ids)
            kwargs["users"] = all_users

        market = MarketInstance(res.json(), *args, **kwargs)

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
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{BASE_URI}/market/history",
                headers=self._headers
                )

        return {datetime.fromisoformat(k): v for k, v in res.items()}

    ## ITEMS

    async def all_items(self) -> List[str]:
        """Get a list of every item.

        Returns
        -------
            List[:class:`str`]
        :return: A list of every item.
        """
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{BASE_URI}/items",
                headers=self._headers
                ).json()

        return res

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
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{BASE_URI}/item/{item}/all",
                headers=self._headers
                )

        return [
            ItemInstance(i["data"]["marketInfo"][item], item, ScanInfo(i["data"]["scInfo"])) 
            for i in res.json()
        ]

    # Roblox
    async def get_users(self, ids: List[int]) -> List[RobloxUser]:
        """Get a list of roblox users from vendor id's.

        Parameters
        ----------
            ids: :class:`List[int]`
                The vendor id's of the users to get.

        Returns
        -------
            :class:`List[User]`
        """
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{BASE_URI}/roblox",
                headers=self._headers,
                json=ids
                )

        return [RobloxUser(u) for u in res.json()]
        

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
        
        
        
