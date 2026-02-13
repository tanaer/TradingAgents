"""Analysis service for running stock analysis."""

import asyncio
import os
import sys
from datetime import datetime
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from ..schemas.analysis import (
    AnalysisRequest,
    AnalysisStatus,
    AnalysisStatusEnum,
    AgentStatus,
    AnalysisReport,
)


class AnalysisService:
    """Service for running stock analysis tasks."""

    def __init__(
        self,
        task_id: str,
        tasks_store: dict[str, AnalysisStatus],
        reports_store: dict[str, AnalysisReport],
    ):
        self.task_id = task_id
        self.tasks_store = tasks_store
        self.reports_store = reports_store

    def _update_status(self, **kwargs):
        """Update task status."""
        if self.task_id in self.tasks_store:
            status = self.tasks_store[self.task_id]
            for key, value in kwargs.items():
                if hasattr(status, key):
                    setattr(status, key, value)
            status.updated_at = datetime.now()

    def _update_agent(self, agent_name: str, **kwargs):
        """Update agent status."""
        if self.task_id in self.tasks_store:
            status = self.tasks_store[self.task_id]
            for agent in status.agents:
                if agent.name == agent_name:
                    for key, value in kwargs.items():
                        if hasattr(agent, key):
                            setattr(agent, key, value)
                    break
            status.updated_at = datetime.now()

    async def run_analysis(self, request: AnalysisRequest):
        """Run the analysis task."""
        try:
            # Update status to running
            self._update_status(status=AnalysisStatusEnum.RUNNING)

            # Set environment variables for the LLM provider
            self._setup_provider_env(request)

            # Import and run the analysis
            report_content = await self._execute_analysis(request)

            # Store the report
            self.reports_store[self.task_id] = AnalysisReport(
                task_id=self.task_id,
                ticker=request.ticker,
                market=request.market,
                analysis_date=request.analysis_date or datetime.now().strftime("%Y-%m-%d"),
                report=report_content,
                created_at=datetime.now(),
            )

            # Update status to completed
            self._update_status(
                status=AnalysisStatusEnum.COMPLETED,
                progress=1.0,
            )

        except Exception as e:
            # Update status to failed
            self._update_status(
                status=AnalysisStatusEnum.FAILED,
            )
            for agent in self.tasks_store[self.task_id].agents:
                if agent.status == "running":
                    agent.status = "failed"
                    agent.message = str(e)

    def _setup_provider_env(self, request: AnalysisRequest):
        """Set up environment variables for the LLM provider."""
        provider = request.llm_provider.lower()

        env_mapping = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY",
            "xai": "XAI_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "zhipu": "ZHIPU_API_KEY",
            "minimax": "MINIMAX_API_KEY",
            "newapi": "NEWAPI_API_KEY",
        }

        if provider in env_mapping:
            env_key = env_mapping[provider]
            # The API key should already be set via /configure endpoint
            # or in the environment

    async def _execute_analysis(self, request: AnalysisRequest) -> str:
        """Execute the actual analysis."""
        from tradingagents.llm_clients.factory import create_llm_client

        # Create LLM clients
        base_url = None
        if request.llm_provider == "newapi":
            base_url = os.environ.get("NEWAPI_BASE_URL")

        shallow_client = create_llm_client(
            provider=request.llm_provider,
            model=request.shallow_model,
            base_url=base_url,
        )

        deep_client = create_llm_client(
            provider=request.llm_provider,
            model=request.deep_model,
            base_url=base_url,
        )

        # Build the analysis report
        report_parts = []
        total_agents = len(request.analysts)
        completed_agents = 0

        for analyst in request.analysts:
            # Update agent status
            self._update_agent(
                analyst.value,
                status="running",
                progress=0.0,
                message="Starting analysis...",
            )

            try:
                # Run the analyst
                result = await self._run_analyst(
                    analyst.value,
                    request.ticker,
                    request.market.value,
                    shallow_client,
                    deep_client,
                )

                report_parts.append(result)

                # Update agent completion
                completed_agents += 1
                overall_progress = completed_agents / total_agents
                self._update_agent(
                    analyst.value,
                    status="completed",
                    progress=1.0,
                    message="Analysis complete",
                )
                self._update_status(progress=overall_progress)

            except Exception as e:
                self._update_agent(
                    analyst.value,
                    status="failed",
                    message=str(e),
                )
                report_parts.append(f"\n## {analyst.value.title()} Analysis\n\nError: {str(e)}\n")

        # Compile final report
        report = self._compile_report(request, report_parts)
        return report

    async def _run_analyst(
        self,
        analyst_type: str,
        ticker: str,
        market: str,
        shallow_client,
        deep_client,
    ) -> str:
        """Run a specific analyst and return its report section."""
        # Simulate agent progress updates
        self._update_agent(analyst_type, progress=0.3, message="Gathering data...")

        # Import analyst modules based on type
        try:
            if analyst_type == "market":
                result = await self._run_market_analyst(ticker, market, shallow_client, deep_client)
            elif analyst_type == "social":
                result = await self._run_social_analyst(ticker, market, shallow_client, deep_client)
            elif analyst_type == "news":
                result = await self._run_news_analyst(ticker, market, shallow_client, deep_client)
            elif analyst_type == "fundamentals":
                result = await self._run_fundamentals_analyst(ticker, market, shallow_client, deep_client)
            else:
                result = f"\n## {analyst_type.title()} Analysis\n\nNot implemented yet.\n"
        except Exception as e:
            result = f"\n## {analyst_type.title()} Analysis\n\nError during analysis: {str(e)}\n"

        self._update_agent(analyst_type, progress=0.9, message="Finalizing report...")
        return result

    async def _run_market_analyst(self, ticker: str, market: str, shallow_client, deep_client) -> str:
        """Run market analyst."""
        import yfinance as yf

        # Get stock data
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1mo")

            # Update progress
            self._update_agent("market", progress=0.5, message="Analyzing market data...")

            # Build market analysis section
            report = f"""
## Market Analyst Report

### Stock Overview
- **Symbol**: {ticker}
- **Company**: {info.get('longName', 'N/A')}
- **Sector**: {info.get('sector', 'N/A')}
- **Industry**: {info.get('industry', 'N/A')}

### Price Information
- **Current Price**: ${info.get('currentPrice', 'N/A')}
- **52 Week High**: ${info.get('fiftyTwoWeekHigh', 'N/A')}
- **52 Week Low**: ${info.get('fiftyTwoWeekLow', 'N/A')}
- **Market Cap**: {info.get('marketCap', 'N/A')}

### Key Metrics
- **P/E Ratio**: {info.get('trailingPE', 'N/A')}
- **Forward P/E**: {info.get('forwardPE', 'N/A')}
- **PEG Ratio**: {info.get('pegRatio', 'N/A')}
- **Price to Book**: {info.get('priceToBook', 'N/A')}
- **Beta**: {info.get('beta', 'N/A')}

### Recent Performance
30-day price range: ${hist['Close'].min():.2f} - ${hist['Close'].max():.2f}

### Analyst Recommendations
{self._format_recommendations(info.get('recommendationKey', 'N/A'))}
"""
            return report
        except Exception as e:
            return f"\n## Market Analyst Report\n\nError fetching market data: {str(e)}\n"

    def _format_recommendations(self, rec: str) -> str:
        """Format recommendation text."""
        recommendations = {
            "strong_buy": "Strong Buy - Analysts strongly recommend buying",
            "buy": "Buy - Analysts recommend buying",
            "hold": "Hold - Analysts recommend holding",
            "sell": "Sell - Analysts recommend selling",
            "strong_sell": "Strong Sell - Analysts strongly recommend selling",
        }
        return recommendations.get(rec, f"Recommendation: {rec}")

    async def _run_social_analyst(self, ticker: str, market: str, shallow_client, deep_client) -> str:
        """Run social media analyst."""
        self._update_agent("social", progress=0.5, message="Analyzing social sentiment...")
        # Placeholder - in production, integrate with social media APIs
        return f"""
## Social Media Analyst Report

### Sentiment Analysis for {ticker}

*Note: This is a placeholder. In production, this would analyze social media sentiment from sources like Twitter, Reddit, etc.*

### Summary
- Overall sentiment analysis would appear here
- Key social media discussions
- Trending topics related to the stock
"""

    async def _run_news_analyst(self, ticker: str, market: str, shallow_client, deep_client) -> str:
        """Run news analyst."""
        self._update_agent("news", progress=0.5, message="Analyzing news coverage...")
        # Placeholder - in production, integrate with news APIs
        return f"""
## News Analyst Report

### Recent News for {ticker}

*Note: This is a placeholder. In production, this would analyze recent news articles.*

### Key Headlines
- Latest news items would appear here
- Impact analysis of news on stock price
- Sentiment from news coverage
"""

    async def _run_fundamentals_analyst(self, ticker: str, market: str, shallow_client, deep_client) -> str:
        """Run fundamentals analyst."""
        import yfinance as yf

        self._update_agent("fundamentals", progress=0.5, message="Analyzing fundamentals...")

        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            return f"""
## Fundamentals Analyst Report

### Financial Health

#### Income Statement Highlights
- **Revenue**: {info.get('totalRevenue', 'N/A')}
- **Net Income**: {info.get('netIncomeToCommon', 'N/A')}
- **EPS (TTM)**: {info.get('trailingEps', 'N/A')}
- **EPS Forward**: {info.get('forwardEps', 'N/A')}

#### Balance Sheet Highlights
- **Total Assets**: {info.get('totalAssets', 'N/A')}
- **Total Debt**: {info.get('totalDebt', 'N/A')}
- **Book Value**: {info.get('bookValue', 'N/A')}
- **Debt to Equity**: {info.get('debtToEquity', 'N/A')}

#### Cash Flow Highlights
- **Operating Cash Flow**: {info.get('operatingCashflow', 'N/A')}
- **Free Cash Flow**: {info.get('freeCashflow', 'N/A')}

### Profitability Metrics
- **Profit Margin**: {info.get('profitMargins', 'N/A')}
- **Operating Margin**: {info.get('operatingMargins', 'N/A')}
- **ROE**: {info.get('returnOnEquity', 'N/A')}
- **ROA**: {info.get('returnOnAssets', 'N/A')}

### Growth Metrics
- **Revenue Growth**: {info.get('revenueGrowth', 'N/A')}
- **Earnings Growth**: {info.get('earningsGrowth', 'N/A')}
- **Quarterly Revenue Growth**: {info.get('quarterlyRevenueGrowth', 'N/A')}

### Valuation
- **Enterprise Value**: {info.get('enterpriseValue', 'N/A')}
- **EV/Revenue**: {info.get('enterpriseToRevenue', 'N/A')}
- **EV/EBITDA**: {info.get('enterpriseToEbitda', 'N/A')}
"""
        except Exception as e:
            return f"\n## Fundamentals Analyst Report\n\nError fetching fundamentals: {str(e)}\n"

    def _compile_report(self, request: AnalysisRequest, parts: list[str]) -> str:
        """Compile the final analysis report."""
        header = f"""# TradingAgents Analysis Report

## Summary
- **Ticker**: {request.ticker}
- **Market**: {request.market.value.upper()}
- **Date**: {request.analysis_date or datetime.now().strftime("%Y-%m-%d")}
- **Analysts**: {', '.join([a.value for a in request.analysts])}

---

"""

        footer = """

---

*Report generated by TradingAgents WebUI*
"""

        return header + "\n".join(parts) + footer
