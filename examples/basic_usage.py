#!/usr/bin/env python3
"""
Basic usage of polymarket-python

Shows how to:
- Look up markets
- Get prices and spreads
- Search for markets
"""

import sys
sys.path.insert(0, '..')

from polymarket import (
    get_market,
    get_event,
    get_price,
    get_spread,
    search_markets,
    get_trending,
    format_price
)


def main():
    print("=" * 60)
    print("  polymarket-python - Basic Usage")
    print("=" * 60)

    # 1. Get a specific market
    print("\n1. Get market by ID")
    print("-" * 40)
    market = get_market("1230810")
    if market:
        print(f"Question: {market['question']}")
        print(f"End date: {market.get('endDate', 'N/A')}")
    else:
        print("Market not found")

    # 2. Get prices
    print("\n2. Get current prices")
    print("-" * 40)
    prices = get_price("1230810")
    print(f"YES: {format_price(prices['yes'])}")
    print(f"NO:  {format_price(prices['no'])}")

    # 3. Get spread
    print("\n3. Check spread (liquidity)")
    print("-" * 40)
    spread = get_spread("1230810", "yes")
    print(f"Best bid: {format_price(spread['bid'])}")
    print(f"Best ask: {format_price(spread['ask'])}")
    print(f"Spread:   {spread['spread']*100:.1f}¢")

    # 4. Search markets
    print("\n4. Search for markets")
    print("-" * 40)
    results = search_markets("bitcoin", limit=3)
    for m in results:
        prices = get_price(m['id'])
        print(f"  {m['question'][:50]}... - YES: {format_price(prices['yes'])}")

    # 5. Trending markets
    print("\n5. Trending by volume")
    print("-" * 40)
    trending = get_trending(limit=5)
    for m in trending:
        vol = float(m.get('volume', 0))
        print(f"  ${vol/1000:.0f}K - {m['question'][:45]}...")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
