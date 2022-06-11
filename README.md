# VIO API Wrapper

##Simple to install 
simply do
`pip install git+https://github.com/WhyDoWeLiveWithoutMeaning/VioWrapper`


##Examples

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