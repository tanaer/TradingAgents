"""Stock search and scanning utilities for full market support."""

import asyncio
from typing import Optional
from datetime import datetime


async def search_us_stocks(query: str, limit: int = 20) -> list[dict]:
    """Search US stocks using yfinance.

    Args:
        query: Search query (symbol or company name)
        limit: Maximum results to return

    Returns:
        List of matching stocks
    """
    try:
        import yfinance as yf
    except ImportError:
        return []

    results = []

    try:
        # Use yfinance search functionality
        # Note: yfinance doesn't have a direct search API, so we'll try common patterns
        ticker = yf.Ticker(query.upper())

        # Try to get info to validate the ticker
        try:
            info = ticker.info
            if info:
                results.append({
                    "symbol": query.upper(),
                    "name": info.get("longName", info.get("shortName", query.upper())),
                    "market": "us",
                    "exchange": info.get("exchange", "NASDAQ/NYSE"),
                    "type": info.get("quoteType", "EQUITY"),
                    "currency": info.get("currency", "USD"),
                })
        except Exception:
            pass

        # Also try common variations
        if len(results) < limit:
            common_suffixes = ["", ".US", "^"]  # Some common patterns
            for suffix in common_suffixes[:1]:  # Only check primary
                try:
                    test_ticker = yf.Ticker(f"{query.upper()}{suffix}")
                    info = test_ticker.info
                    if info and info.get("quoteType") == "EQUITY":
                        symbol = query.upper()
                        if symbol not in [r["symbol"] for r in results]:
                            results.append({
                                "symbol": symbol,
                                "name": info.get("longName", info.get("shortName", symbol)),
                                "market": "us",
                                "exchange": info.get("exchange", "NASDAQ/NYSE"),
                                "type": "EQUITY",
                                "currency": info.get("currency", "USD"),
                            })
                except Exception:
                    continue

    except Exception as e:
        print(f"US stock search error: {e}")

    return results[:limit]


async def search_hk_stocks(query: str, limit: int = 20) -> list[dict]:
    """Search Hong Kong stocks using yfinance.

    Args:
        query: Search query (symbol or company name)
        limit: Maximum results to return

    Returns:
        List of matching stocks
    """
    try:
        import yfinance as yf
    except ImportError:
        return []

    results = []
    query_num = query.replace(".", "").replace("HK", "").zfill(4)

    # Common HK stock patterns
    patterns = [
        f"{query_num}.HK",
        f"{query}.HK",
    ]

    for pattern in patterns:
        if len(results) >= limit:
            break
        try:
            ticker = yf.Ticker(pattern)
            info = ticker.info
            if info and info.get("quoteType") == "EQUITY":
                results.append({
                    "symbol": pattern,
                    "name": info.get("longName", info.get("shortName", pattern)),
                    "market": "hk",
                    "exchange": "HKEX",
                    "type": "EQUITY",
                    "currency": "HKD",
                })
        except Exception:
            continue

    return results[:limit]


async def search_cn_stocks(query: str, limit: int = 20) -> list[dict]:
    """Search Chinese A-share stocks using akshare.

    Args:
        query: Search query (symbol or company name)
        limit: Maximum results to return

    Returns:
        List of matching stocks
    """
    try:
        import akshare as ak
    except ImportError:
        return []

    results = []

    try:
        # Get all A-share stocks
        df = ak.stock_zh_a_spot_em()

        # Search by code or name
        query_lower = query.lower()
        mask = (
            df["代码"].str.contains(query, case=False, na=False) |
            df["名称"].str.contains(query, case=False, na=False)
        )
        matches = df[mask].head(limit)

        for _, row in matches.iterrows():
            code = row["代码"]
            # Determine market (SH vs SZ)
            if code.startswith("6"):
                market = "SH"
            elif code.startswith(("0", "3")):
                market = "SZ"
            elif code.startswith(("4", "8")):
                market = "BJ"  # Beijing Stock Exchange
            else:
                market = "SZ"

            results.append({
                "symbol": f"{code}.{market}",
                "name": row["名称"],
                "market": "cn",
                "exchange": f"{market}SE",
                "type": "A-SHARE",
                "currency": "CNY",
                "price": float(row.get("最新价", 0)) if row.get("最新价") else None,
            })

    except Exception as e:
        print(f"CN stock search error: {e}")

    return results


async def scan_popular_us_stocks() -> list[dict]:
    """Scan popular US stocks."""
    popular_symbols = [
        ("AAPL", "Apple Inc."),
        ("MSFT", "Microsoft Corporation"),
        ("GOOGL", "Alphabet Inc."),
        ("AMZN", "Amazon.com Inc."),
        ("NVDA", "NVIDIA Corporation"),
        ("TSLA", "Tesla Inc."),
        ("META", "Meta Platforms Inc."),
        ("BRK.B", "Berkshire Hathaway"),
        ("JPM", "JPMorgan Chase"),
        ("V", "Visa Inc."),
        ("JNJ", "Johnson & Johnson"),
        ("WMT", "Walmart Inc."),
        ("PG", "Procter & Gamble"),
        ("MA", "Mastercard Inc."),
        ("UNH", "UnitedHealth Group"),
        ("HD", "Home Depot"),
        ("DIS", "Walt Disney"),
        ("PYPL", "PayPal Holdings"),
        ("NFLX", "Netflix Inc."),
        ("ADBE", "Adobe Inc."),
        ("CRM", "Salesforce Inc."),
        ("INTC", "Intel Corporation"),
        ("AMD", "AMD Inc."),
        ("QCOM", "Qualcomm Inc."),
    ]

    return [
        {"symbol": s, "name": n, "market": "us", "exchange": "NASDAQ/NYSE"}
        for s, n in popular_symbols
    ]


async def scan_popular_hk_stocks() -> list[dict]:
    """Scan popular Hong Kong stocks."""
    popular_symbols = [
        ("0700.HK", "腾讯控股"),
        ("9988.HK", "阿里巴巴"),
        ("3690.HK", "美团"),
        ("1810.HK", "小米集团"),
        ("2318.HK", "中国平安"),
        ("0005.HK", "汇丰控股"),
        ("1299.HK", "友邦保险"),
        ("0941.HK", "中国移动"),
        ("0388.HK", "香港交易所"),
        ("0883.HK", "中国海洋石油"),
        ("2382.HK", "舜宇光学科技"),
        ("2020.HK", "安踏体育"),
        ("2269.HK", "药明生物"),
        ("1177.HK", "中国生物制药"),
        ("1928.HK", "金沙中国"),
    ]

    return [
        {"symbol": s, "name": n, "market": "hk", "exchange": "HKEX"}
        for s, n in popular_symbols
    ]


async def scan_popular_cn_stocks() -> list[dict]:
    """Scan popular Chinese A-share stocks using akshare."""
    try:
        import akshare as ak
    except ImportError:
        # Fallback to hardcoded list
        popular_symbols = [
            ("600519.SH", "贵州茅台"),
            ("000858.SZ", "五粮液"),
            ("601318.SH", "中国平安"),
            ("600036.SH", "招商银行"),
            ("000001.SZ", "平安银行"),
            ("601166.SH", "兴业银行"),
            ("600000.SH", "浦发银行"),
            ("000651.SZ", "格力电器"),
            ("000333.SZ", "美的集团"),
            ("601398.SH", "工商银行"),
        ]
        return [
            {"symbol": s, "name": n, "market": "cn", "exchange": "SSE/SZSE"}
            for s, n in popular_symbols
        ]

    try:
        # Get real-time data and sort by volume or amount
        df = ak.stock_zh_a_spot_em()

        # Sort by trading amount (成交额) to get most active stocks
        if "成交额" in df.columns:
            df = df.sort_values("成交额", ascending=False)

        results = []
        for _, row in df.head(20).iterrows():
            code = row["代码"]
            if code.startswith("6"):
                market = "SH"
            elif code.startswith(("0", "3")):
                market = "SZ"
            else:
                market = "BJ"

            results.append({
                "symbol": f"{code}.{market}",
                "name": row["名称"],
                "market": "cn",
                "exchange": f"{market}SE",
                "price": float(row.get("最新价", 0)) if row.get("最新价") else None,
                "change_pct": float(row.get("涨跌幅", 0)) if row.get("涨跌幅") else None,
            })

        return results

    except Exception:
        return []


async def search_all_markets(query: str, market: Optional[str] = None, limit: int = 20) -> list[dict]:
    """Search stocks across all markets.

    Args:
        query: Search query
        market: Optional market filter ('us', 'hk', 'cn')
        limit: Maximum total results

    Returns:
        List of matching stocks from all markets
    """
    results = []
    per_market_limit = limit // 3 if not market else limit

    tasks = []

    if market is None or market == "us":
        tasks.append(("us", search_us_stocks(query, per_market_limit)))
    if market is None or market == "hk":
        tasks.append(("hk", search_hk_stocks(query, per_market_limit)))
    if market is None or market == "cn":
        tasks.append(("cn", search_cn_stocks(query, per_market_limit)))

    for market_type, task in tasks:
        try:
            market_results = await task
            results.extend(market_results)
        except Exception as e:
            print(f"Error searching {market_type}: {e}")

    return results[:limit]
