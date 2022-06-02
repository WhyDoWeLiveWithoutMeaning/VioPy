import websockets
import requests
import asyncio

from datetime import datetime
from terminaltables import AsciiTable
from itertools import zip_longest

from typing import (
    Union,
    List,
    Dict,
)

BASE_URI = "http://adv.vi-o.tech/api"

class ItemSummary:
    """Summary Instance

    Represents the instance of the summary of an Item
    """

    def __init__(self, data: dict) -> None:
        self.buy_volume: int = data["buy"].get("Volume", 0)
        self.buy_price: int = data["buy"].get("Best", 0)
        self.sell_volume: int = data["sell"].get("Volume", 0)
        self.sell_price: int = data["sell"].get("Best", 0)

    def _ascii_table(self) -> list:
        return [
            ["", "Sell Volume", "Sell Price", "Buy Volume", "Buy Price", ""],
            ["", self.sell_volume, self.sell_price, self.buy_volume, self.buy_price, ""]
        ]

class Listing:
    """Listing Instance

    Represents the instance of a single listing
    """

    def __init__(self, data: dict) -> None:
        self.id: int = data["userID"]
        self.volume: int = data["amount"]
        self.price: int = data["price"]

    def to_list(self) -> List[int]:
        return [self.id, self.volume, self.price]

class ItemListings:
    """Listings Instance

    Represents the instance of the listings of an Item
    """

    def __init__(self, data: dict) -> None:
        self.buy: List[Listing] = [Listing(i) for i in data["buy"]]
        self.sell: List[Listing] = [Listing(i) for i in data["sell"]]

    def _ascii_table(self) -> list:
        return [["", "Sell Orders", "", "", "Buy Orders", ""]] + \
            [ i[0] + i[1]
            for i in zip_longest(
                [i.to_list() for i in self.buy],
                [i.to_list() for i in self.sell],
                fillvalue=["", "", ""]
            )
        ]
        

class ItemInstance:
    """Item Instance

    Represents the instance of an item.
    """

    def __init__(self, data: dict, item: str):
        self.item = item
        self.listings = ItemListings(data["listings"])
        self.summary = ItemSummary(data["summary"])

    def __str__(self) -> str:
        table = self.summary._ascii_table() + self.listings._ascii_table()
        str_tab = AsciiTable(table, title=self.item).table.split("\n")
        str_tab.insert(4, str_tab[2])
        str_tab.insert(6, str_tab[2])
        return "\n".join(str_tab)


class ScanInfo:
    """Scan information

    Represents the information about a scan.
    """

    def __init__(self, data: dict):
        self.unix: int = data["capturedTime"]
        self.datetime: datetime = data["datetimeSaved"]

class MarketInstance:
    """Market Instance

    Represents one instance of the market
    """

    def __init__(self, data: dict) -> None:
        self.id = data["_id"]
        self.scan_info: ScanInfo = ScanInfo(data["data"]["scInfo"])
        self.items: Dict[str, ItemInstance] = {}
        for k, v in data["data"]["marketInfo"].items():
            self.items[k] = ItemInstance(v, k)

    def __getattr__(self, item: str) -> Union[ItemInstance, None]:
        return self.items.get(item, None)

    def __getitem__(self, item: str) -> Union[ItemInstance, None]:
        return self.items.get(item, None)

class Vio:
    """ Vio Class

    Represents an instance of the vio API, with a certain key.
    """

    def __init__(self, key: str) -> None:
        """Initialize the Vio Object

        Args:
            key: The API key to use.
        
        """
        self.key = key
        
        self._headers = {
            "X-API-KEY": self.key,
        }

        res = requests.get(
            f"{BASE_URI}/market",
            headers=self._headers
            ).json()

        self._latest_market = MarketInstance(res)

    @property
    def current(self): 
        """Get the current market

        Returns:
            The current market.
        """
        return self._latest_market

class AsyncVio:
    
    def __init__(self, key: str) -> None:
        self.key = key
        self._headers = {
            "X-API-KEY": self.key,
        }

    async def current_market(self) -> MarketInstance:
        res = requests.get(
            f"{BASE_URI}/market",
            headers=self._headers
            ).json()
        return MarketInstance(res)