"""Market data router."""

from fastapi import APIRouter, HTTPException, Query

from ..config import MARKET_CONFIG
from ..schemas.market import MarketInfo, StockSearchResult, PopularStock
from .stock_search import (
    search_all_markets,
    scan_popular_us_stocks,
    scan_popular_hk_stocks,
    scan_popular_cn_stocks,
)

router = APIRouter()


@router.get("", response_model=list[MarketInfo])
async def list_markets() -> list[MarketInfo]:
    """List all supported markets."""
    return [
        MarketInfo(
            id=market_id,
            name=config["name"],
            data_source=config["data_source"],
            symbol_format=config["symbol_format"],
            description=config["description"],
        )
        for market_id, config in MARKET_CONFIG.items()
    ]


@router.get("/search", response_model=list[StockSearchResult])
async def search_stocks(
    query: str = Query(..., min_length=1, description="Search query"),
    market: str | None = Query(None, description="Filter by market (us/hk/cn)"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
) -> list[StockSearchResult]:
    """Search for stocks by symbol or name across all markets.

    Uses real-time data from:
    - US/HK: yfinance
    - CN (A-share): akshare
    """
    results = await search_all_markets(query, market, limit)

    return [
        StockSearchResult(
            symbol=r["symbol"],
            name=r["name"],
            market=r["market"],
            exchange=r.get("exchange"),
        )
        for r in results
    ]


@router.get("/{market}/popular", response_model=list[PopularStock])
async def get_popular_stocks(market: str) -> list[PopularStock]:
    """Get popular/most active stocks for a specific market.

    For CN market, returns real-time most active stocks by trading volume.
    """
    if market not in MARKET_CONFIG:
        raise HTTPException(status_code=404, detail=f"Market '{market}' not found")

    if market == "us":
        stocks = await scan_popular_us_stocks()
    elif market == "hk":
        stocks = await scan_popular_hk_stocks()
    elif market == "cn":
        stocks = await scan_popular_cn_stocks()
    else:
        stocks = []

    return [
        PopularStock(
            symbol=s["symbol"],
            name=s["name"],
            market=s["market"],
            price=s.get("price"),
            change_percent=s.get("change_pct"),
        )
        for s in stocks
    ]


@router.get("/{market}/scan")
async def scan_market(market: str, top_n: int = Query(50, ge=10, le=200)):
    """Scan market for top stocks by activity.

    Args:
        market: Market to scan (us/hk/cn)
        top_n: Number of top stocks to return

    Returns:
        List of top active stocks
    """
    if market not in MARKET_CONFIG:
        raise HTTPException(status_code=404, detail=f"Market '{market}' not found")

    if market == "cn":
        # Only CN market supports real-time scanning via akshare
        stocks = await scan_popular_cn_stocks()
        return {
            "market": market,
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "stocks": stocks[:top_n],
        }
    else:
        # For US/HK, return popular stocks list
        if market == "us":
            stocks = await scan_popular_us_stocks()
        else:
            stocks = await scan_popular_hk_stocks()

        return {
            "market": market,
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "stocks": stocks[:top_n],
            "note": "Pre-defined popular stocks list. Real-time scanning available for CN market only.",
        }
