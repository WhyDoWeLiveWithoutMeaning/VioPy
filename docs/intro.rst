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

We want this program to get the current state of the market!

Here is the code:

.. code-block:: python3

    # Import Vio
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

Asynchronous Program
~~~~~~~~~~~~~~~~~~~~

Let's write a basic asynchronous program!

Let's make it print average the best buy price of Korrelite in the market
and let's also subscribe to the websocket event to get real-time data.

.. code-block:: python3

    import asyncio
    from vio import AsyncVio, MarketInstance # import AsyncVio and also the MarketInstance Object

    # Initializing the Vio Object
    v = AsyncVio("Your API Key")

    # Creating the function that listens to the real-time data
    @v.event # We use the @v.event decorator to tell the Vio Object that this function will be listening
    async def on_market_update(market: MarketInstance):
        print("The market has just been updated!")

        # Print Korrelite when we get an update
        print(market["Korrelite"])


    # Our main function
    async def main():

        # Initiating the ws to listen for the real-time data
        await v.listen()

        # Getting every scan of Korrelite
        korrelite_history = await v.item_history("Korrelite")

        # Using a loop to put all the prices in a list
        prices = [instance.summary.buy_price for instance in korrelite_history]

        # Calculating the average price
        average_price = sum(prices) / len(prices)

        # Printing the average price
        print(average_price)

    # Run the event loop with the main function
    asyncio.run(main())

Very simple and easy to use!