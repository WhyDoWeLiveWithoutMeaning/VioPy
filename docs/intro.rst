.. currentmodule:: Introduction

Introduction to the Vio API
============================

Welcome to VioPy a modern and easy to use Python Wrapper for the Vio API.

With the ability to use the Vio API in Python, you can easily integrate 
your own Starscape Market Data Feed into your own programs.

We have features such as:

* **Real-time Data** - Get real-time data from the Vio API through the websocket.
* **Historical Data** - Get historical data from the Vio API.
* **Asychronous Support** - using ``async`` and ``await``.

This Wrapper is also written by Meaning#0001.
Creator of the Vio API.

Getting Started
---------------

Installing VioPy
~~~~~~~~~~~~~~~~~

You can install VioPy by using the following command:
``pip install vio``

Basic Program
~~~~~~~~~~~~~~

Let's write a basic program!

.. code-block:: python3

    from vio import Vio

    # Initializing the Vio Object
    vio = Vio("Your API Key")

    # Getting the current market
    market = vio.current()

    # Getting a specific Item from the market
    item = market["Korrelite"]

    # Printing the item
    print(item)

This basic example should show you how to use the Vio API in Python.


Registering an event
---------------------

.. code-block:: python3

    @vio.event
    async def print_market(market: MarketInstance):
        print(market["Korrelite"])