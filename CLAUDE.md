# CLAUDE.md

> Instructions for Claude Code and other AI agents working with this library.

## What is this?

A clean Python wrapper for Polymarket's three APIs. Use it to get market data and place trades without thinking about API details.

## Quick start

```bash
pip install -r requirements.txt
python
```

```python
from polymarket import *

# Read-only operations (no auth needed)
market = get_market("1230810")
prices = get_price("1230810")
spread = get_spread("1230810", "yes")
```

## Function map

### Read-only (no auth)

| Function | Purpose | Returns |
|----------|---------|---------|
| `get_market(id)` | Market by ID | dict with question, prices |
| `get_event(slug)` | Event from URL | dict with markets list |
| `search_markets(query)` | Search | list of markets |
| `get_trending(limit)` | Top volume | list of markets |
| `get_price(id)` | Current prices | `{'yes': 0.65, 'no': 0.35}` |
| `get_spread(id, outcome)` | Bid/ask spread | `{'bid': 0.64, 'ask': 0.66, 'spread': 0.02}` |
| `get_orderbook(token_id)` | Full book | `{'bids': [...], 'asks': [...]}` |
| `get_token_id(id, outcome)` | Token for trading | token_id string |
| `get_market_by_token(token_id)` | Reverse lookup | dict with question, outcome |
| `get_trades(id)` | Recent trades | list of trades |
| `get_positions(address)` | Wallet positions | list of positions |
| `get_leaderboard()` | Top traders | list |

### Trading (requires auth)

| Function | Purpose |
|----------|---------|
| `create_client(...)` | Get authenticated client |
| `place_order(client, token, side, price, size)` | Limit order |
| `cancel_order(client, order_id)` | Cancel one |
| `cancel_all(client)` | Cancel all |
| `get_open_orders(client)` | List orders |
| `get_balance(client)` | USDC balance |

### Helpers

| Function | Example |
|----------|---------|
| `format_price(0.35)` | `"35¢"` |
| `parse_price("35c")` | `0.35` |

## Price format

- Internal: `0.35` (decimal)
- Display: `35¢` (use `format_price()`)
- NEVER percentages

## Token IDs

Markets have two tokens: YES and NO. You need the token_id for:
- Orderbook lookups
- Placing trades

```python
yes_token = get_token_id("1230810", "yes")
no_token = get_token_id("1230810", "no")
```

## APIs used

| API | Base URL | Purpose |
|-----|----------|---------|
| Gamma | gamma-api.polymarket.com | Markets, events |
| CLOB | clob.polymarket.com | Orderbooks, trading |
| Data | data-api.polymarket.com | Trades, positions |

## Do

- Use `get_token_id()` before orderbook or trading calls
- Check spread before trading (wide spread = illiquid)
- Handle None returns (market not found)

## Don't

- Don't confuse market_id with token_id
- Don't use percentages (35% ≠ 35¢)
- Don't spam APIs (rate limits apply)
