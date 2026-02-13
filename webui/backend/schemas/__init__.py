"""Pydantic schemas for API request/response models."""

from .provider import (
    ProviderInfo,
    ProviderConfig,
    ProviderTestRequest,
    ProviderTestResponse,
)
from .analysis import (
    AnalysisRequest,
    AnalysisStatus,
    AnalysisProgress,
    AnalysisReport,
)
from .market import (
    MarketInfo,
    StockSearchResult,
    PopularStock,
)

__all__ = [
    # Provider schemas
    "ProviderInfo",
    "ProviderConfig",
    "ProviderTestRequest",
    "ProviderTestResponse",
    # Analysis schemas
    "AnalysisRequest",
    "AnalysisStatus",
    "AnalysisProgress",
    "AnalysisReport",
    # Market schemas
    "MarketInfo",
    "StockSearchResult",
    "PopularStock",
]
