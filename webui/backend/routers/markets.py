"""Market data router."""

from fastapi import APIRouter, HTTPException, Query

from ..config import MARKET_CONFIG
from ..schemas.market import MarketInfo, StockSearchResult, PopularStock

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
    limit: int = Query(10, ge=1, le=50, description="Max results"),
) -> list[StockSearchResult]:
    """Search for stocks by symbol or name."""
    results = []

    query_lower = query.lower()

    # Search in different markets
    markets_to_search = [market] if market else list(MARKET_CONFIG.keys())

    for market_id in markets_to_search:
        if market_id not in MARKET_CONFIG:
            continue

        try:
            if market_id == "us":
                results.extend(_search_us_stocks(query_lower, limit))
            elif market_id == "hk":
                results.extend(_search_hk_stocks(query_lower, limit))
            elif market_id == "cn":
                results.extend(_search_cn_stocks(query_lower, limit))
        except Exception:
            # Log error but continue with other markets
            pass

    return results[:limit]


@router.get("/{market}/popular", response_model=list[PopularStock])
async def get_popular_stocks(market: str) -> list[PopularStock]:
    """Get popular stocks for a specific market."""
    if market not in MARKET_CONFIG:
        raise HTTPException(status_code=404, detail=f"Market '{market}' not found")

    # Return predefined popular stocks for each market
    popular_stocks = {
        "us": [
            PopularStock(symbol="AAPL", name="Apple Inc.", market="us"),
            PopularStock(symbol="MSFT", name="Microsoft Corporation", market="us"),
            PopularStock(symbol="GOOGL", name="Alphabet Inc.", market="us"),
            PopularStock(symbol="AMZN", name="Amazon.com Inc.", market="us"),
            PopularStock(symbol="NVDA", name="NVIDIA Corporation", market="us"),
            PopularStock(symbol="TSLA", name="Tesla Inc.", market="us"),
            PopularStock(symbol="META", name="Meta Platforms Inc.", market="us"),
            PopularStock(symbol="BRK.B", name="Berkshire Hathaway", market="us"),
        ],
        "hk": [
            PopularStock(symbol="0700.HK", name="腾讯控股", market="hk"),
            PopularStock(symbol="9988.HK", name="阿里巴巴", market="hk"),
            PopularStock(symbol="3690.HK", name="美团", market="hk"),
            PopularStock(symbol="1810.HK", name="小米集团", market="hk"),
            PopularStock(symbol="2318.HK", name="中国平安", market="hk"),
            PopularStock(symbol="0005.HK", name="汇丰控股", market="hk"),
            PopularStock(symbol="1299.HK", name="友邦保险", market="hk"),
            PopularStock(symbol="0941.HK", name="中国移动", market="hk"),
        ],
        "cn": [
            PopularStock(symbol="600519.SH", name="贵州茅台", market="cn"),
            PopularStock(symbol="000858.SZ", name="五粮液", market="cn"),
            PopularStock(symbol="601318.SH", name="中国平安", market="cn"),
            PopularStock(symbol="600036.SH", name="招商银行", market="cn"),
            PopularStock(symbol="000001.SZ", name="平安银行", market="cn"),
            PopularStock(symbol="601166.SH", name="兴业银行", market="cn"),
            PopularStock(symbol="600000.SH", name="浦发银行", market="cn"),
            PopularStock(symbol="000651.SZ", name="格力电器", market="cn"),
        ],
    }

    return popular_stocks.get(market, [])


def _search_us_stocks(query: str, limit: int) -> list[StockSearchResult]:
    """Search US stocks using yfinance or similar."""
    # Simplified implementation - in production, use a proper stock API
    us_stocks = {
        "aapl": ("AAPL", "Apple Inc."),
        "msft": ("MSFT", "Microsoft Corporation"),
        "googl": ("GOOGL", "Alphabet Inc."),
        "amzn": ("AMZN", "Amazon.com Inc."),
        "nvda": ("NVDA", "NVIDIA Corporation"),
        "tsla": ("TSLA", "Tesla Inc."),
        "meta": ("META", "Meta Platforms Inc."),
        "google": ("GOOGL", "Alphabet Inc."),
        "apple": ("AAPL", "Apple Inc."),
        "microsoft": ("MSFT", "Microsoft Corporation"),
    }

    results = []
    for key, (symbol, name) in us_stocks.items():
        if query in key or query in symbol.lower() or query in name.lower():
            results.append(StockSearchResult(
                symbol=symbol,
                name=name,
                market="us",
                exchange="NASDAQ/NYSE",
            ))
            if len(results) >= limit:
                break

    return results


def _search_hk_stocks(query: str, limit: int) -> list[StockSearchResult]:
    """Search Hong Kong stocks."""
    hk_stocks = {
        "0700": ("0700.HK", "腾讯控股"),
        "9988": ("9988.HK", "阿里巴巴"),
        "3690": ("3690.HK", "美团"),
        "1810": ("1810.HK", "小米集团"),
        "腾讯": ("0700.HK", "腾讯控股"),
        "阿里": ("9988.HK", "阿里巴巴"),
        "美团": ("3690.HK", "美团"),
        "小米": ("1810.HK", "小米集团"),
    }

    results = []
    for key, (symbol, name) in hk_stocks.items():
        if query in key or query in name:
            results.append(StockSearchResult(
                symbol=symbol,
                name=name,
                market="hk",
                exchange="HKEX",
            ))
            if len(results) >= limit:
                break

    return results


def _search_cn_stocks(query: str, limit: int) -> list[StockSearchResult]:
    """Search Chinese A-share stocks."""
    cn_stocks = {
        "600519": ("600519.SH", "贵州茅台"),
        "000858": ("000858.SZ", "五粮液"),
        "601318": ("601318.SH", "中国平安"),
        "600036": ("600036.SH", "招商银行"),
        "茅台": ("600519.SH", "贵州茅台"),
        "五粮液": ("000858.SZ", "五粮液"),
        "平安": ("601318.SH", "中国平安"),
        "招行": ("600036.SH", "招商银行"),
    }

    results = []
    for key, (symbol, name) in cn_stocks.items():
        if query in key or query in name:
            results.append(StockSearchResult(
                symbol=symbol,
                name=name,
                market="cn",
                exchange="SSE/SZSE",
            ))
            if len(results) >= limit:
                break

    return results
