"""
Polymarket Python SDK

Clean, simple API wrapper for Polymarket prediction markets.
No bloat. No magic. Just functions that work.
"""

import os
import json
import urllib.request
import ssl
from pathlib import Path
from decimal import Decimal
from typing import Optional, Dict, List, Any

# API Endpoints
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"
DATA_API = "https://data-api.polymarket.com"

# SSL context for requests
_SSL_CTX = ssl.create_default_context()

# Token ID cache for reverse lookups
_TOKEN_CACHE: Dict[str, dict] = {}


def _request(url: str, timeout: int = 10) -> Any:
    """Make HTTP GET request and return JSON."""
    req = urllib.request.Request(url, headers={
        'User-Agent': 'polymarket-python/1.0'
    })
    with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as resp:
        return json.loads(resp.read())


# ==============================================================================
# MARKET DATA
# ==============================================================================

def get_market(market_id: str) -> Optional[dict]:
    """Get market info by ID.

    Args:
        market_id: Market ID (numeric string like "1230810")

    Returns:
        Market dict with question, prices, etc. or None if not found.

    Example:
        >>> market = get_market("1230810")
        >>> print(market['question'])
        'Will Trump win the 2024 election?'
    """
    data = _request(f"{GAMMA_API}/markets?id={market_id}")
    if data and len(data) > 0:
        market = data[0]
        # Parse clobTokenIds if it's a string
        if 'clobTokenIds' in market and isinstance(market['clobTokenIds'], str):
            market['clobTokenIds'] = json.loads(market['clobTokenIds'])
        return market
    return None


def get_event(slug: str) -> Optional[dict]:
    """Get event by URL slug.

    Args:
        slug: Event slug from Polymarket URL
              e.g., "trump-election-2024" from polymarket.com/event/trump-election-2024

    Returns:
        Event dict with markets list, or None if not found.

    Example:
        >>> event = get_event("trump-election-2024")
        >>> for m in event['markets']:
        ...     print(m['question'], m['outcomePrices'])
    """
    data = _request(f"{GAMMA_API}/events?slug={slug}")
    if data and len(data) > 0:
        return data[0]
    return None


def search_markets(query: str, limit: int = 10) -> List[dict]:
    """Search markets by keyword.

    Args:
        query: Search term
        limit: Max results (default 10)

    Returns:
        List of market dicts matching query.

    Example:
        >>> markets = search_markets("bitcoin", limit=5)
        >>> for m in markets:
        ...     print(m['question'])
    """
    url = f"{GAMMA_API}/markets?_limit={limit}&active=true&closed=false"
    data = _request(url)
    if not data:
        return []

    query_lower = query.lower()
    return [m for m in data if query_lower in m.get('question', '').lower()]


def get_trending(limit: int = 10) -> List[dict]:
    """Get trending markets by volume.

    Args:
        limit: Max results (default 10)

    Returns:
        List of market dicts sorted by volume.
    """
    url = f"{GAMMA_API}/markets?_limit={limit}&active=true&closed=false&order=volume&ascending=false"
    return _request(url) or []


# ==============================================================================
# PRICES & ORDERBOOK
# ==============================================================================

def get_price(market_id: str) -> Dict[str, float]:
    """Get current YES/NO prices for a market.

    Args:
        market_id: Market ID

    Returns:
        Dict with 'yes' and 'no' prices as floats (0.0 to 1.0)

    Example:
        >>> prices = get_price("1230810")
        >>> print(f"YES: {prices['yes']*100:.0f}¢, NO: {prices['no']*100:.0f}¢")
        YES: 65¢, NO: 35¢
    """
    market = get_market(market_id)
    if not market:
        return {'yes': 0.0, 'no': 0.0}

    # Parse outcomePrices
    prices_str = market.get('outcomePrices', '[]')
    if isinstance(prices_str, str):
        prices = json.loads(prices_str)
    else:
        prices = prices_str

    return {
        'yes': float(prices[0]) if len(prices) > 0 else 0.0,
        'no': float(prices[1]) if len(prices) > 1 else 0.0
    }


def get_orderbook(token_id: str) -> dict:
    """Get orderbook for a token.

    Args:
        token_id: CLOB token ID (not market_id - use get_token_id first)

    Returns:
        Dict with 'bids' and 'asks' lists, each containing [price, size] pairs.

    Example:
        >>> token = get_token_id("1230810", "yes")
        >>> book = get_orderbook(token)
        >>> print(f"Best bid: {book['bids'][0]}")
    """
    data = _request(f"{CLOB_API}/book?token_id={token_id}")
    return {
        'bids': data.get('bids', []),
        'asks': data.get('asks', [])
    }


def get_spread(market_id: str, outcome: str = "yes") -> Dict[str, float]:
    """Get bid/ask spread for a market outcome.

    Args:
        market_id: Market ID
        outcome: "yes" or "no"

    Returns:
        Dict with 'bid', 'ask', 'spread' as floats.

    Example:
        >>> spread = get_spread("1230810", "yes")
        >>> print(f"Bid: {spread['bid']*100:.0f}¢, Ask: {spread['ask']*100:.0f}¢")
        >>> print(f"Spread: {spread['spread']*100:.1f}¢")
    """
    token = get_token_id(market_id, outcome)
    if not token:
        return {'bid': 0.0, 'ask': 0.0, 'spread': 1.0}

    book = get_orderbook(token)

    best_bid = float(book['bids'][0]['price']) if book['bids'] else 0.0
    best_ask = float(book['asks'][0]['price']) if book['asks'] else 1.0

    return {
        'bid': best_bid,
        'ask': best_ask,
        'spread': best_ask - best_bid
    }


# ==============================================================================
# TOKEN IDS
# ==============================================================================

def get_token_id(market_id: str, outcome: str = "yes") -> Optional[str]:
    """Get CLOB token ID for a market outcome.

    The token ID is required for orderbook lookups and trading.

    Args:
        market_id: Market ID
        outcome: "yes" or "no"

    Returns:
        Token ID string, or None if not found.

    Example:
        >>> yes_token = get_token_id("1230810", "yes")
        >>> no_token = get_token_id("1230810", "no")
    """
    market = get_market(market_id)
    if not market or 'clobTokenIds' not in market:
        return None

    tokens = market['clobTokenIds']
    # tokens[0] = YES, tokens[1] = NO
    return tokens[0] if outcome.lower() == "yes" else tokens[1]


def get_market_by_token(token_id: str) -> Optional[dict]:
    """Reverse lookup: get market info from token ID.

    Useful when you have positions or orders by token_id and need market details.

    Args:
        token_id: CLOB token ID

    Returns:
        Dict with 'question', 'outcome' (YES/NO), 'slug', etc.
    """
    if token_id in _TOKEN_CACHE:
        return _TOKEN_CACHE[token_id]

    data = _request(f"{GAMMA_API}/markets?clob_token_ids={token_id}")
    if data and len(data) > 0:
        market = data[0]
        tokens = market.get('clobTokenIds', [])
        if isinstance(tokens, str):
            tokens = json.loads(tokens)

        result = {
            'question': market.get('question', 'Unknown'),
            'outcome': 'YES' if tokens and tokens[0] == token_id else 'NO',
            'slug': market.get('slug', ''),
            'market_id': market.get('id', ''),
            'endDate': market.get('endDate', ''),
        }
        _TOKEN_CACHE[token_id] = result
        return result

    return None


# ==============================================================================
# ACTIVITY DATA
# ==============================================================================

def get_trades(market_id: str, limit: int = 50) -> List[dict]:
    """Get recent trades for a market.

    Args:
        market_id: Market ID
        limit: Max trades to return

    Returns:
        List of trade dicts with 'price', 'size', 'side', 'timestamp'.
    """
    token = get_token_id(market_id, "yes")
    if not token:
        return []

    data = _request(f"{DATA_API}/trades?asset_id={token}&limit={limit}")
    return data or []


def get_positions(address: str) -> List[dict]:
    """Get positions for a wallet address.

    Args:
        address: Ethereum wallet address

    Returns:
        List of position dicts with 'token_id', 'size', 'market' info.
    """
    data = _request(f"{DATA_API}/positions?user={address}")
    return data or []


def get_leaderboard(limit: int = 20) -> List[dict]:
    """Get top traders by profit.

    Args:
        limit: Max results

    Returns:
        List of trader dicts with 'address', 'profit', 'volume'.
    """
    data = _request(f"{DATA_API}/leaderboard?limit={limit}")
    return data or []


# ==============================================================================
# TRADING (requires py-clob-client)
# ==============================================================================

def create_client(
    private_key: str,
    api_key: str,
    api_secret: str,
    api_passphrase: str,
    funder: str,
    host: str = CLOB_API,
    chain_id: int = 137
):
    """Create authenticated CLOB client for trading.

    Requires py-clob-client: pip install py-clob-client

    Args:
        private_key: Your wallet private key (keep secret!)
        api_key: API key from Polymarket
        api_secret: API secret
        api_passphrase: API passphrase
        funder: Your Polymarket proxy wallet address
        host: CLOB API host (default: production)
        chain_id: Polygon chain ID (137 for mainnet)

    Returns:
        Authenticated ClobClient instance.

    Example:
        >>> client = create_client(
        ...     private_key=os.getenv("POLYMARKET_KEY"),
        ...     api_key="...",
        ...     api_secret="...",
        ...     api_passphrase="...",
        ...     funder="0x..."
        ... )
        >>> balance = client.get_balance()
    """
    try:
        from py_clob_client.client import ClobClient
        from py_clob_client.clob_types import ApiCreds
    except ImportError:
        raise ImportError("Install py-clob-client: pip install py-clob-client")

    creds = ApiCreds(
        api_key=api_key,
        api_secret=api_secret,
        api_passphrase=api_passphrase
    )

    return ClobClient(
        host,
        chain_id,
        key=private_key,
        creds=creds,
        signature_type=2,  # GNOSIS_SAFE for Polymarket proxy wallets
        funder=funder
    )


def place_order(
    client,
    token_id: str,
    side: str,
    price: float,
    size: int
) -> dict:
    """Place a limit order.

    Args:
        client: Authenticated ClobClient
        token_id: Token to trade (use get_token_id first)
        side: "BUY" or "SELL"
        price: Price as decimal (0.35 = 35 cents)
        size: Number of shares

    Returns:
        Order response dict.

    Example:
        >>> token = get_token_id("1230810", "yes")
        >>> result = place_order(client, token, "BUY", 0.35, 10)
        >>> print(f"Order status: {result['status']}")
    """
    from py_clob_client.clob_types import OrderArgs, OrderType
    from py_clob_client.order_builder.constants import BUY, SELL

    order_args = OrderArgs(
        price=price,
        size=size,
        side=BUY if side.upper() == "BUY" else SELL,
        token_id=token_id
    )

    signed_order = client.create_order(order_args)
    return client.post_order(signed_order, OrderType.GTC)


def cancel_order(client, order_id: str) -> dict:
    """Cancel an order.

    Args:
        client: Authenticated ClobClient
        order_id: Order ID to cancel

    Returns:
        Cancellation response.
    """
    return client.cancel(order_id)


def cancel_all(client) -> dict:
    """Cancel all open orders.

    Args:
        client: Authenticated ClobClient

    Returns:
        Cancellation response.
    """
    return client.cancel_all()


def get_open_orders(client) -> List[dict]:
    """Get all open orders.

    Args:
        client: Authenticated ClobClient

    Returns:
        List of open order dicts.
    """
    return client.get_orders()


def get_balance(client) -> dict:
    """Get account balances.

    Args:
        client: Authenticated ClobClient

    Returns:
        Balance dict with USDC amount.
    """
    return client.get_balance()


# ==============================================================================
# HELPERS
# ==============================================================================

def format_price(price: float) -> str:
    """Format price as cents.

    Example:
        >>> format_price(0.35)
        '35¢'
    """
    return f"{price * 100:.0f}¢"


def parse_price(price_str: str) -> float:
    """Parse price string to decimal.

    Accepts: "35c", "35¢", "35 cents", "0.35", ".35"

    Example:
        >>> parse_price("35c")
        0.35
    """
    s = price_str.lower().strip()
    s = s.replace('¢', '').replace('c', '').replace('cents', '').strip()

    val = float(s)
    # If it looks like cents (> 1), convert to decimal
    if val > 1:
        val = val / 100

    return val
