"""Market-related schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class MarketInfo(BaseModel):
    """Information about a market."""

    id: str = Field(..., description="Market identifier (us/hk/cn)")
    name: str = Field(..., description="Display name")
    data_source: str = Field(..., description="Data source name")
    symbol_format: str = Field(..., description="Example symbol format")
    description: str = Field(..., description="Market description")


class StockSearchResult(BaseModel):
    """Result from stock search."""

    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company name")
    market: str = Field(..., description="Market identifier")
    exchange: Optional[str] = Field(None, description="Exchange name")


class PopularStock(BaseModel):
    """Popular stock information."""

    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company name")
    market: str = Field(..., description="Market identifier")
    price: Optional[float] = Field(None, description="Current price")
    change_percent: Optional[float] = Field(None, description="Price change percentage")
