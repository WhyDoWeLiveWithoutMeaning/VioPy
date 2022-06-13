.. currentmodule:: Introduction

Introduction to the Vio API
============================


Registering an event
---------------------

.. code-block:: python
    @vio.event
    async def print_market(market: MarketInstance):
        print(market["Korrelite"])