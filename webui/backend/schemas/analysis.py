"""Analysis-related schemas."""

from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AnalysisStatusEnum(str, Enum):
    """Analysis task status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class MarketType(str, Enum):
    """Market type."""

    US = "us"
    HK = "hk"
    CN = "cn"


class AnalystType(str, Enum):
    """Analyst type."""

    MARKET = "market"
    SOCIAL = "social"
    NEWS = "news"
    FUNDAMENTALS = "fundamentals"


class AnalysisRequest(BaseModel):
    """Request to start an analysis."""

    ticker: str = Field(..., description="Stock ticker symbol")
    market: MarketType = Field(MarketType.US, description="Market type")
    analysts: list[AnalystType] = Field(
        default=[AnalystType.MARKET],
        description="List of analysts to use",
    )
    analysis_date: Optional[str] = Field(
        None,
        description="Analysis date in YYYY-MM-DD format (defaults to today)",
    )
    research_depth: int = Field(
        3,
        ge=1,
        le=5,
        description="Research depth (1-5)",
    )
    llm_provider: str = Field(..., description="LLM provider to use")
    shallow_model: str = Field(..., description="Model for quick thinking")
    deep_model: str = Field(..., description="Model for deep thinking")


class AgentStatus(BaseModel):
    """Status of an individual agent."""

    name: str = Field(..., description="Agent name")
    status: str = Field(..., description="Agent status (pending/running/completed/failed)")
    progress: float = Field(0.0, ge=0.0, le=1.0, description="Progress (0-1)")
    message: Optional[str] = Field(None, description="Current activity message")


class AnalysisStatus(BaseModel):
    """Status of an analysis task."""

    task_id: str = Field(..., description="Task identifier")
    status: AnalysisStatusEnum = Field(..., description="Overall status")
    progress: float = Field(0.0, ge=0.0, le=1.0, description="Overall progress (0-1)")
    agents: list[AgentStatus] = Field(
        default_factory=list,
        description="Status of individual agents",
    )
    created_at: datetime = Field(..., description="Task creation time")
    updated_at: datetime = Field(..., description="Last update time")


class AnalysisProgress(BaseModel):
    """Real-time analysis progress update."""

    task_id: str = Field(..., description="Task identifier")
    event_type: str = Field(
        ...,
        description="Event type (agent_start/agent_progress/agent_complete/report_update/error)",
    )
    agent_name: Optional[str] = Field(None, description="Agent that generated this event")
    progress: float = Field(0.0, ge=0.0, le=1.0, description="Progress (0-1)")
    message: Optional[str] = Field(None, description="Status message")
    report_chunk: Optional[str] = Field(None, description="Partial report content")


class AnalysisReport(BaseModel):
    """Complete analysis report."""

    task_id: str = Field(..., description="Task identifier")
    ticker: str = Field(..., description="Stock ticker symbol")
    market: MarketType = Field(..., description="Market type")
    analysis_date: str = Field(..., description="Analysis date")
    report: str = Field(..., description="Full analysis report in markdown")
    created_at: datetime = Field(..., description="Report generation time")
