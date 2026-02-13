"""Server-Sent Events (SSE) utilities."""

import asyncio
import json
from datetime import datetime
from typing import AsyncGenerator

from ..schemas.analysis import AnalysisStatus, AnalysisStatusEnum, AnalysisReport


async def event_stream(
    task_id: str,
    tasks_store: dict[str, AnalysisStatus],
    reports_store: dict[str, AnalysisReport],
    interval: float = 1.0,
) -> AsyncGenerator[str, None]:
    """Generate SSE event stream for analysis progress."""

    last_progress = 0.0
    last_status = None

    while True:
        if task_id not in tasks_store:
            yield f"event: error\ndata: {json.dumps({'message': 'Task not found'})}\n\n"
            break

        status = tasks_store[task_id]

        # Send status update if changed
        if status.status != last_status or status.progress != last_progress:
            event_data = {
                "task_id": task_id,
                "status": status.status.value,
                "progress": status.progress,
                "agents": [
                    {
                        "name": agent.name,
                        "status": agent.status,
                        "progress": agent.progress,
                        "message": agent.message,
                    }
                    for agent in status.agents
                ],
                "timestamp": datetime.now().isoformat(),
            }
            yield f"event: status\ndata: {json.dumps(event_data)}\n\n"

            last_status = status.status
            last_progress = status.progress

        # Send report if completed
        if status.status == AnalysisStatusEnum.COMPLETED and task_id in reports_store:
            report = reports_store[task_id]
            report_data = {
                "task_id": task_id,
                "ticker": report.ticker,
                "market": report.market.value,
                "report": report.report,
                "created_at": report.created_at.isoformat(),
            }
            yield f"event: report\ndata: {json.dumps(report_data)}\n\n"
            break

        # Send error if failed
        if status.status == AnalysisStatusEnum.FAILED:
            yield f"event: error\ndata: {json.dumps({'message': 'Analysis failed'})}\n\n"
            break

        # Keep connection alive
        yield f"event: ping\ndata: {json.dumps({'timestamp': datetime.now().isoformat()})}\n\n"

        await asyncio.sleep(interval)
