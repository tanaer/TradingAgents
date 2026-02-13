"""Eastmoney data provider for Chinese news and market data."""

from typing import Optional
from datetime import datetime
import re


def get_cn_stock_news(
    symbol: str,
    limit: int = 20,
) -> list[dict]:
    """Get news for a Chinese A-share stock.

    Args:
        symbol: Stock symbol in format '000001.SZ' or '600000.SH'
        limit: Maximum number of news items

    Returns:
        List of news items with title, summary, source, date, url
    """
    try:
        import akshare as ak
    except ImportError:
        raise ImportError("akshare is required for news data. Install with: pip install akshare")

    code, _ = _parse_cn_symbol(symbol)

    try:
        # Get stock news from Eastmoney
        df = ak.stock_news_em(symbol=code)

        if df.empty:
            return []

        news_items = []
        for _, row in df.head(limit).iterrows():
            news_items.append({
                "title": row.get("新闻标题", ""),
                "summary": row.get("新闻内容", "")[:200] if row.get("新闻内容") else "",
                "source": row.get("来源", ""),
                "date": row.get("发布时间", ""),
                "url": row.get("新闻链接", ""),
            })

        return news_items

    except Exception as e:
        raise RuntimeError(f"Failed to fetch news for {symbol}: {str(e)}")


def get_cn_market_news(
    market: str = "a股",
    limit: int = 30,
) -> list[dict]:
    """Get general market news for Chinese markets.

    Args:
        market: Market type ('a股', '港股', '美股')
        limit: Maximum number of news items

    Returns:
        List of news items
    """
    try:
        import akshare as ak
    except ImportError:
        raise ImportError("akshare is required for news data. Install with: pip install akshare")

    try:
        # Get financial news from Eastmoney
        df = ak.stock_news_em(symbol="财经新闻")

        if df.empty:
            return []

        news_items = []
        for _, row in df.head(limit).iterrows():
            news_items.append({
                "title": row.get("新闻标题", ""),
                "summary": row.get("新闻内容", "")[:200] if row.get("新闻内容") else "",
                "source": row.get("来源", ""),
                "date": row.get("发布时间", ""),
                "url": row.get("新闻链接", ""),
            })

        return news_items

    except Exception as e:
        raise RuntimeError(f"Failed to fetch market news: {str(e)}")


def get_cn_stock_notices(
    symbol: str,
    notice_type: Optional[str] = None,
    limit: int = 20,
) -> list[dict]:
    """Get company announcements/notices for a Chinese A-share stock.

    Args:
        symbol: Stock symbol in format '000001.SZ' or '600000.SH'
        notice_type: Type of notice (None for all)
        limit: Maximum number of notices

    Returns:
        List of notices
    """
    try:
        import akshare as ak
    except ImportError:
        raise ImportError("akshare is required for notice data. Install with: pip install akshare")

    code, _ = _parse_cn_symbol(symbol)

    try:
        # Get company announcements
        df = ak.stock_notice_report(symbol=code)

        if df.empty:
            return []

        notices = []
        for _, row in df.head(limit).iterrows():
            notices.append({
                "title": row.get("公告标题", ""),
                "type": row.get("公告类型", ""),
                "date": row.get("公告日期", ""),
                "url": row.get("公告链接", ""),
            })

        return notices

    except Exception as e:
        raise RuntimeError(f"Failed to fetch notices for {symbol}: {str(e)}")


def get_cn_stock_research_reports(
    symbol: str,
    limit: int = 10,
) -> list[dict]:
    """Get analyst research reports for a Chinese A-share stock.

    Args:
        symbol: Stock symbol in format '000001.SZ' or '600000.SH'
        limit: Maximum number of reports

    Returns:
        List of research reports
    """
    try:
        import akshare as ak
    except ImportError:
        raise ImportError("akshare is required for research reports. Install with: pip install akshare")

    code, _ = _parse_cn_symbol(symbol)

    try:
        # Get research reports
        df = ak.stock_research_report_em(symbol=code)

        if df.empty:
            return []

        reports = []
        for _, row in df.head(limit).iterrows():
            reports.append({
                "title": row.get("研究报告名称", ""),
                "rating": row.get("评级", ""),
                "institution": row.get("研究机构", ""),
                "analyst": row.get("分析师", ""),
                "date": row.get("发布日期", ""),
            })

        return reports

    except Exception as e:
        raise RuntimeError(f"Failed to fetch research reports for {symbol}: {str(e)}")


def get_cn_stock_sentiment(symbol: str) -> dict:
    """Get market sentiment indicators for a Chinese A-share stock.

    Args:
        symbol: Stock symbol in format '000001.SZ' or '600000.SH'

    Returns:
        Dictionary with sentiment indicators
    """
    try:
        import akshare as ak
    except ImportError:
        raise ImportError("akshare is required for sentiment data. Install with: pip install akshare")

    code, _ = _parse_cn_symbol(symbol)

    try:
        # Get stock comments/discussions from Eastmoney
        df = ak.stock_comment_em(symbol=code)

        if df.empty:
            return {"sentiment": "neutral", "score": 50}

        # Calculate sentiment based on comments
        total = len(df)
        bullish = len(df[df["情绪"] == "看涨"]) if "情绪" in df.columns else 0
        bearish = len(df[df["情绪"] == "看跌"]) if "情绪" in df.columns else 0

        if total > 0:
            score = int((bullish / total) * 100)
        else:
            score = 50

        if score >= 70:
            sentiment = "bullish"
        elif score >= 55:
            sentiment = "slightly_bullish"
        elif score >= 45:
            sentiment = "neutral"
        elif score >= 30:
            sentiment = "slightly_bearish"
        else:
            sentiment = "bearish"

        return {
            "symbol": symbol,
            "sentiment": sentiment,
            "score": score,
            "bullish_count": bullish,
            "bearish_count": bearish,
            "total_comments": total,
        }

    except Exception as e:
        # Return neutral sentiment if data not available
        return {
            "symbol": symbol,
            "sentiment": "neutral",
            "score": 50,
            "error": str(e),
        }


def _parse_cn_symbol(symbol: str) -> tuple[str, str]:
    """Parse Chinese stock symbol to code and market."""
    if "." in symbol:
        code, market = symbol.split(".")
        return code, market.upper()
    else:
        code = symbol
        if symbol.startswith("6"):
            market = "SH"
        else:
            market = "SZ"
        return code, market
