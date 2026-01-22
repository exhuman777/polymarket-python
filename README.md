# polymarket-python

**A Python wrapper for Polymarket that doesn't make you think.**

I got tired of reading docs every time I wanted to check a price or place an order. This wraps the three Polymarket APIs into functions that do what you'd expect.

## Who this is for

- **Python developers** building trading tools
- **Data folks** who want market data without the ceremony
- **AI agents** (Claude, GPT) that need clean function signatures

## Who this is NOT for

- **Beginners** - You should understand Polymarket first
- **Production trading** - This is a convenience wrapper, not a trading system
- **High-frequency** - No websocket support, just HTTP

## Install

```bash
pip install polymarket-python
```

Or clone and use directly:

```bash
git clone https://github.com/exhuman777/polymarket-python.git
cd polymarket-python
pip install -r requirements.txt
```

## Quick look

```python
from polymarket import *

# Get a market
market = get_market("1230810")
print(market['question'])  # "Will Trump win?"

# Get prices
prices = get_price("1230810")
print(f"YES: {format_price(prices['yes'])}")  # "YES: 65¢"

# Check spread
spread = get_spread("1230810", "yes")
print(f"Bid: {spread['bid']*100:.0f}¢, Ask: {spread['ask']*100:.0f}¢")

# Search markets
markets = search_markets("bitcoin", limit=5)
for m in markets:
    print(m['question'])
```

## Functions

### Market Data

| Function | What it does |
|----------|--------------|
| `get_market(id)` | Get market by ID |
| `get_event(slug)` | Get event from URL slug |
| `search_markets(query)` | Search by keyword |
| `get_trending(limit)` | Top markets by volume |

### Prices

| Function | What it does |
|----------|--------------|
| `get_price(id)` | YES/NO prices |
| `get_orderbook(token_id)` | Full orderbook |
| `get_spread(id, outcome)` | Bid/ask/spread |

### Token IDs

Every market has two token IDs (one for YES, one for NO). You need these for orderbooks and trading.

| Function | What it does |
|----------|--------------|
| `get_token_id(id, "yes")` | Get token ID for outcome |
| `get_market_by_token(token_id)` | Reverse lookup |

### Activity

| Function | What it does |
|----------|--------------|
| `get_trades(id)` | Recent trades |
| `get_positions(address)` | Wallet positions |
| `get_leaderboard()` | Top traders |

### Trading

Trading requires `py-clob-client` and API credentials from Polymarket.

```python
# Create authenticated client
client = create_client(
    private_key="0x...",
    api_key="...",
    api_secret="...",
    api_passphrase="...",
    funder="0x..."  # Your Polymarket proxy wallet
)

# Get token ID first
token = get_token_id("1230810", "yes")

# Place order: BUY 10 @ 35¢
result = place_order(client, token, "BUY", 0.35, 10)

# Check orders
orders = get_open_orders(client)

# Cancel
cancel_all(client)
```

## Price format

Prices are decimals internally: `0.35` = 35 cents

Use helpers:
```python
format_price(0.35)      # "35¢"
parse_price("35c")      # 0.35
parse_price("0.35")     # 0.35
```

## The three APIs

This wrapper talks to three Polymarket APIs:

| API | URL | What it has |
|-----|-----|-------------|
| **Gamma** | gamma-api.polymarket.com | Markets, events, prices |
| **CLOB** | clob.polymarket.com | Orderbooks, trading |
| **Data** | data-api.polymarket.com | Trades, positions, leaderboard |

## Limitations

- **No websockets** - Polling only. For real-time, use the raw CLOB websocket.
- **No auth caching** - You manage your own client lifecycle.
- **Rate limits apply** - Polymarket limits ~100 req/min per IP.
- **Polygon only** - Chain ID 137 (mainnet). No testnet.

## Related

- [yesno-events](https://github.com/exhuman777/yesno-events) - Full trading terminal
- [claude-trader](https://github.com/exhuman777/claude-trader) - Natural language trading with Claude Code

## License

MIT
