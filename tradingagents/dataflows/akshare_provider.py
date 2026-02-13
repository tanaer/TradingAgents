"""Akshare data provider for Chinese A-share market data."""

import pandas as pd
from typing import Optional
from datetime import datetime, timedelta


def get_cn_stock_data(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Get Chinese A-share stock OHLCV data.

    Args:
        symbol: Stock symbol in format '000001.SZ' or '600000.SH'
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        DataFrame with OHLCV data
    """
    try:
        import akshare as ak
    except ImportError:
        raise ImportError("akshare is required for A-share data. Install with: pip install akshare")

    # Parse symbol to get code and market
    code, market = _parse_cn_symbol(symbol)

    # Set default dates
    if not end_date:
        end_date = datetime.now().strftime("%Y%m%d")
    else:
        end_date = end_date.replace("-", "")

    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
    else:
        start_date = start_date.replace("-", "")

    # Get data from akshare
    try:
        df = ak.stock_zh_a_hist(
            symbol=code,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq",  # Forward adjusted price
        )

        # Standardize column names
        df = df.rename(columns={
            "日期": "date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
            "成交额": "amount",
            "振幅": "amplitude",
            "涨跌幅": "change_pct",
            "涨跌额": "change",
            "换手率": "turnover",
        })

        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
        df = df.sort_index()

        return df[["open", "high", "low", "close", "volume"]]

    except Exception as e:
        raise RuntimeError(f"Failed to fetch A-share data for {symbol}: {str(e)}")


def get_cn_stock_info(symbol: str) -> dict:
    """Get Chinese A-share stock basic information.

    Args:
        symbol: Stock symbol in format '000001.SZ' or '600000.SH'

    Returns:
        Dictionary with stock information
    """
    try:
        import akshare as ak
    except ImportError:
        raise ImportError("akshare is required for A-share data. Install with: pip install akshare")

    code, market = _parse_cn_symbol(symbol)

    try:
        # Get stock info
        df = ak.stock_individual_info_em(symbol=code)

        info = {}
        for _, row in df.iterrows():
            info[row["item"]] = row["value"]

        return {
            "symbol": symbol,
            "code": code,
            "market": market,
            "name": info.get("股票简称", ""),
            "industry": info.get("行业", ""),
            "list_date": info.get("上市时间", ""),
            "total_share": info.get("总市值", ""),
            "circulating_share": info.get("流通市值", ""),
        }

    except Exception as e:
        raise RuntimeError(f"Failed to fetch stock info for {symbol}: {str(e)}")


def get_cn_stock_fundamentals(symbol: str) -> dict:
    """Get Chinese A-share stock fundamental data.

    Args:
        symbol: Stock symbol in format '000001.SZ' or '600000.SH'

    Returns:
        Dictionary with fundamental data
    """
    try:
        import akshare as ak
    except ImportError:
        raise ImportError("akshare is required for A-share data. Install with: pip install akshare")

    code, _ = _parse_cn_symbol(symbol)

    try:
        # Get financial indicators
        df = ak.stock_financial_abstract_ths(symbol=code, indicator="按报告期")

        if df.empty:
            return {}

        # Get latest data
        latest = df.iloc[0]

        return {
            "report_date": latest.get("报告期", ""),
            "revenue": latest.get("营业收入", ""),
            "net_profit": latest.get("净利润", ""),
            "total_assets": latest.get("总资产", ""),
            "total_liabilities": latest.get("总负债", ""),
            "shareholder_equity": latest.get("股东权益", ""),
            "roe": latest.get("净资产收益率", ""),
            "gross_margin": latest.get("销售毛利率", ""),
            "net_margin": latest.get("销售净利率", ""),
            "pe_ratio": latest.get("市盈率", ""),
            "pb_ratio": latest.get("市净率", ""),
        }

    except Exception as e:
        raise RuntimeError(f"Failed to fetch fundamentals for {symbol}: {str(e)}")


def search_cn_stocks(keyword: str, limit: int = 10) -> list[dict]:
    """Search Chinese A-share stocks by keyword.

    Args:
        keyword: Search keyword (stock code or name)
        limit: Maximum number of results

    Returns:
        List of matching stocks
    """
    try:
        import akshare as ak
    except ImportError:
        raise ImportError("akshare is required for A-share data. Install with: pip install akshare")

    try:
        # Get all A-share stocks
        df = ak.stock_zh_a_spot_em()

        # Search by code or name
        mask = (
            df["代码"].str.contains(keyword, case=False, na=False) |
            df["名称"].str.contains(keyword, case=False, na=False)
        )
        results = df[mask].head(limit)

        stocks = []
        for _, row in results.iterrows():
            code = row["代码"]
            market = "SH" if code.startswith("6") else "SZ"
            stocks.append({
                "symbol": f"{code}.{market}",
                "code": code,
                "name": row["名称"],
                "market": market,
                "price": row.get("最新价"),
                "change_pct": row.get("涨跌幅"),
            })

        return stocks

    except Exception as e:
        raise RuntimeError(f"Failed to search stocks: {str(e)}")


def get_cn_stock_realtime(symbol: str) -> dict:
    """Get real-time Chinese A-share stock data.

    Args:
        symbol: Stock symbol in format '000001.SZ' or '600000.SH'

    Returns:
        Dictionary with real-time data
    """
    try:
        import akshare as ak
    except ImportError:
        raise ImportError("akshare is required for A-share data. Install with: pip install akshare")

    code, _ = _parse_cn_symbol(symbol)

    try:
        df = ak.stock_zh_a_spot_em()
        stock = df[df["代码"] == code]

        if stock.empty:
            raise ValueError(f"Stock {symbol} not found")

        row = stock.iloc[0]

        return {
            "symbol": symbol,
            "code": code,
            "name": row["名称"],
            "price": row.get("最新价"),
            "open": row.get("今开"),
            "high": row.get("最高"),
            "low": row.get("最低"),
            "volume": row.get("成交量"),
            "amount": row.get("成交额"),
            "change_pct": row.get("涨跌幅"),
            "change": row.get("涨跌额"),
            "turnover": row.get("换手率"),
        }

    except Exception as e:
        raise RuntimeError(f"Failed to fetch real-time data for {symbol}: {str(e)}")


def _parse_cn_symbol(symbol: str) -> tuple[str, str]:
    """Parse Chinese stock symbol to code and market.

    Args:
        symbol: Symbol in format '000001.SZ' or '600000.SH'

    Returns:
        Tuple of (code, market)
    """
    if "." in symbol:
        code, market = symbol.split(".")
        return code, market.upper()
    else:
        # Infer market from code
        code = symbol
        if symbol.startswith("6"):
            market = "SH"
        else:
            market = "SZ"
        return code, market
