# AGENTS.md

## Overview

Python client for Polymarket APIs. Wraps CLOB, Gamma, and Data APIs.

## Commands

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/ -v
```

## Files

```
polymarket-python/
  polymarket.py      # Main client
  examples/          # Usage examples
  tests/             # pytest tests
```

## API Endpoints

```python
# Gamma (market data)
"https://gamma-api.polymarket.com/markets"
"https://gamma-api.polymarket.com/events"

# CLOB (trading)
"https://clob.polymarket.com/book"
"https://clob.polymarket.com/orders"

# Data (positions, trades)
"https://data-api.polymarket.com/trades"
"https://data-api.polymarket.com/positions"
```

## Price Format

- Internal: `0.35` (decimal, 0.00-1.00)
- Display: `35¢` (cents)
- Never percentages

## Code Style

- Python: `ruff format` + `ruff check`
- Type hints required
- Docstrings for public functions

## Testing

```bash
python -m pytest tests/ -v
python -m pytest tests/test_client.py -v  # Specific
```

## Don't

- Commit credentials
- Spam APIs (rate limits exist)
- Confuse price with percentage

## Related

- `~/Rufus/projects/claude-trader/` - Trading bot
- `~/Rufus/projects/yesno-events/` - Terminal
