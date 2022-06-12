# VIO API Wrapper

## Simple to install 
simply do
`pip install git+https://github.com/WhyDoWeLiveWithoutMeaning/VioWrapper`


## Examples

### Getting the Current Market

#### Code
```python
from vio import Vio

# Initialize the Vio object with your API key.
v = Vio("KEY")

# Get the current market.
current_market = v.current()

# Print the current market for Korrelite
print(current_market["Korrelite"])
```

#### Output

```
+Korrelite---+-------------+------------+------------+------------+------+
|            | Sell Volume | Sell Price | Buy Volume | Buy Price  |      |
+------------+-------------+------------+------------+------------+------+
|            | 363006      | 4.45       | 1595761    | 3.7        |      |
+------------+-------------+------------+------------+------------+------+
| 162066609  | 6452        | 4.65       | 120400875  | 14058      | 3.5  |       
| 650846808  | 12968       | 4.7        | 108285033  | 999958     | 3.5  |       
| 173250721  | 32501       | 4.75       | 428485469  | 16000      | 3.5  |       
| 3363298512 | 7645        | 4.95       | 2700713836 | 86155      | 3.45 |       
| 2239255818 | 6583        | 6.9        | 650846808  | 102106     | 3.35 |       
|            |             |            | 1248486511 | 180661     | 3.2  |       
+------------+-------------+------------+------------+------------+------+ 
```

### Getting the History of an Item

#### Code

```python
from vio import Vio

# Initialize the Vio object with your API key.
v = Vio("KEY")

# Get the history of Korrelite.
korrelite_history = v.item_history("Korrelite")

# Create a list of Buy Prices
sell_prices = [i.summary.buy_price for i in korrelite_history]

# Print the average buy price.
print(sum(sell_prices)/len(sell_prices))
```

#### Output

```
3.518448940269686
```

### Example of Discord Market Bot using VioWrapper

#### Code
```python
import discord
from discord import app_commands
from discord.ext import commands

from datetime import datetime

from vio import AsyncVio

intents = discord.Intents.default()
intents.members = True
intents.presences = True

class TestBot(commands.Bot):
    def __init__(self, v) -> None:
        super().__init__(
            command_prefix="!",
            application_id=10000000000001, # Replace with your Application ID
            intents=intents,
            case_insensitive=True,
            )
        self.vio = v

    async def on_ready(self) -> None:
        print("Bot is ready.")
        await self.vio.listen() # Start listening for market data

    async def setup_hook(self) -> None:
        await self.tree.sync()

v = AsyncVio("Vio KEY") # Replace with your VIO Api Key
client = TestBot(v)

def number_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

def market_to_embed(market: MarketInstance):
    embed = discord.Embed(
        title=f"{market.item} Market",
        description=f"Scanned at: {discord.utils.format_dt(datetime.fromtimestamp(market.scan_info.unix), style='R')}",
    )
    embed.add_field(name="Best Sell Price", value=str(market.summary.sell_price), inline=True)
    embed.add_field(name="Best Buy Price", value=str(market.summary.buy_price), inline=True)
    embed.add_field(name="Market Volume", value=f'{number_format(market.summary.sell_volume)}/{number_format(market.summary.buy_volume)}', inline=True)
    embed.add_field(name="Sell Orders", value="\n".join(f"{order.volume:,.0f} @ {order.price:,.2f} from {order.id}" for order in market.listings.sell), inline=False)
    embed.add_field(name="Buy Orders", value="\n".join(f"{order.volume:,.0f} @ {order.price:,.2f} from {order.id}" for order in market.listings.buy))
    return embed

@client.vio.event
async def on_market_update(market: MarketInstance):
    channel = await client.fetch_channel(TEST_CHANNEL) # Replace with your channel ID

    # Process ItemInstance to an embed
    embed = market_to_embed(market["Korrelite"])

    # Send the embed to the channel
    await channel.send(embed=embed)

@client.tree.command()
async def market(interaction: discord.Interaction, item: str):
    """Market Item Search
    Get the Current Market Listings of a Specific Item
    """

    # Get the current Market
    current_market = await v.current()

    # Get the item requested from the market
    market = current_market[item]

    # Process the ItemMarket instance into an embed
    embed = market_to_embed(market)

    # Send the embed to the user
    await interaction.response.send_message(embed=embed)

@market.autocomplete("item")
async def market_autocomplete(interaction: discord.Interaction, current: str):
    itemlist = [
            app_commands.Choice(name=i, value=i)
            for i in ["Korrelite", "Reknite", "Axnit", "RedNarcor", "Narcor", "Water", "Vexnium"] if i.lower().startswith(current.lower())
        ]
    return itemlist


client.run("BOT_TOKEN") # Replace with your Bot Token
```

#### Output

![Example of Command Being Run](https://i.imgur.com/YgXflIN.png)
