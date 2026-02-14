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

    # Basic settings
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

    # Research depth settings
    research_depth: int = Field(
        3,
        ge=1,
        le=5,
        description="Research depth (1-5, affects debate rounds)",
    )
    max_debate_rounds: int = Field(
        1,
        ge=1,
        le=10,
        description="Maximum debate rounds between Bull/Bear researchers",
    )
    max_risk_discuss_rounds: int = Field(
        1,
        ge=1,
        le=10,
        description="Maximum risk discussion rounds",
    )

    # LLM configuration
    llm_provider: str = Field(..., description="LLM provider to use")
    shallow_model: str = Field(..., description="Model for quick thinking")
    deep_model: str = Field(..., description="Model for deep thinking")

    # Advanced LLM settings
    temperature: Optional[float] = Field(
        None,
        ge=0.0,
        le=2.0,
        description="Model temperature (0.0-2.0)",
    )
    openai_reasoning_effort: Optional[str] = Field(
        None,
        description="OpenAI reasoning effort (low/medium/high)",
    )
    google_thinking_level: Optional[str] = Field(
        None,
        description="Google thinking level (minimal/high)",
    )

    # Data vendor settings
    data_vendor: Optional[str] = Field(
        "yfinance",
        description="Data vendor (yfinance/alpha_vantage)",
    )

    # Agent swarm settings
    enable_bull_bear_debate: bool = Field(
        True,
        description="Enable Bull/Bear researcher debate",
    )
    enable_risk_analysis: bool = Field(
        True,
        description="Enable risk debators (aggressive/conservative/neutral)",
    )


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
    current_phase: Optional[str] = Field(None, description="Current analysis phase")
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
    phase: Optional[str] = Field(None, description="Current phase (analysis/debate/risk/trading)")
    progress: float = Field(0.0, ge=0.0, le=1.0, description="Progress (0-1)")
    message: Optional[str] = Field(None, description="Status message")
    report_chunk: Optional[str] = Field(None, description="Partial report content")


class AnalysisReport(BaseModel):
    """Complete analysis report."""

    task_id: str = Field(..., description="Task identifier")
    ticker: str = Field(..., description="Stock ticker symbol")
    market: MarketType = Field(..., description="Market type")
    analysis_date: str = Field(..., description="Analysis date")

    # Report sections
    executive_summary: Optional[str] = Field(None, description="Executive summary")
    full_report: str = Field(..., description="Full analysis report in markdown")

    # Analysis metadata
    analysts_used: list[str] = Field(default_factory=list, description="Analysts used")
    debate_rounds: int = Field(0, description="Number of debate rounds")
    risk_discussion_rounds: int = Field(0, description="Number of risk discussion rounds")

    # Trading signals
    final_decision: Optional[str] = Field(None, description="Final trading decision")
    confidence_level: Optional[float] = Field(None, description="Confidence level (0-1)")

    created_at: datetime = Field(..., description="Report generation time")


class AnalysisConfig(BaseModel):
    """Configuration options for analysis."""

    # Research depth presets
    depth_presets: dict = Field(
        default={
            "shallow": {"debate_rounds": 1, "risk_rounds": 1, "description": "Quick analysis"},
            "medium": {"debate_rounds": 3, "risk_rounds": 2, "description": "Balanced analysis"},
            "deep": {"debate_rounds": 5, "risk_rounds": 3, "description": "Comprehensive analysis"},
        },
        description="Research depth presets",
    )

    # Available analysts
    available_analysts: list[dict] = Field(
        default=[
            {"id": "market", "name": "Market Analyst", "description": "Technical analysis and price trends"},
            {"id": "social", "name": "Social Media Analyst", "description": "Social sentiment analysis"},
            {"id": "news", "name": "News Analyst", "description": "News impact analysis"},
            {"id": "fundamentals", "name": "Fundamentals Analyst", "description": "Financial fundamentals"},
        ],
        description="Available analyst types",
    )

    # Agent swarm info
    agent_swarm_description: str = Field(
        default="The system uses a multi-agent architecture:\n"
        "1. **Analysts** (Market/Social/News/Fundamentals): Gather and analyze data\n"
        "2. **Researchers** (Bull/Bear): Debate findings from different perspectives\n"
        "3. **Research Manager**: Synthesizes debate into insights\n"
        "4. **Trader**: Makes trading recommendations\n"
        "5. **Risk Debators** (Aggressive/Conservative/Neutral): Evaluate risk\n"
        "6. **Risk Judge**: Final risk assessment",
        description="Agent swarm architecture description",
    )
