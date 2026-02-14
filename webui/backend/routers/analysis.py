"""Analysis task router."""

import asyncio
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse

from ..schemas.analysis import (
    AnalysisRequest,
    AnalysisStatus,
    AnalysisStatusEnum,
    AgentStatus,
    AnalysisReport,
    AnalysisConfig,
)
from ..services.analysis_service import AnalysisService

router = APIRouter()

# In-memory task storage (use Redis in production)
_tasks: dict[str, AnalysisStatus] = {}
_reports: dict[str, AnalysisReport] = {}


@router.get("/config", response_model=AnalysisConfig)
async def get_analysis_config() -> AnalysisConfig:
    """Get analysis configuration options and presets."""
    return AnalysisConfig()


@router.post("/start", response_model=dict[str, str])
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    """Start a new analysis task."""
    task_id = str(uuid.uuid4())

    # Initialize task status
    now = datetime.now()
    _tasks[task_id] = AnalysisStatus(
        task_id=task_id,
        status=AnalysisStatusEnum.PENDING,
        progress=0.0,
        agents=[
            AgentStatus(name=analyst.value, status="pending", progress=0.0)
            for analyst in request.analysts
        ],
        created_at=now,
        updated_at=now,
    )

    # Start background analysis
    service = AnalysisService(task_id, _tasks, _reports)
    background_tasks.add_task(service.run_analysis, request)

    return {"task_id": task_id, "message": "Analysis started"}


@router.get("/status/{task_id}", response_model=AnalysisStatus)
async def get_analysis_status(task_id: str) -> AnalysisStatus:
    """Get the status of an analysis task."""
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    return _tasks[task_id]


@router.get("/stream/{task_id}")
async def stream_analysis_progress(task_id: str) -> StreamingResponse:
    """Stream analysis progress using Server-Sent Events (SSE)."""
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    from ..utils.sse import event_stream

    return StreamingResponse(
        event_stream(task_id, _tasks, _reports),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/report/{task_id}", response_model=AnalysisReport)
async def get_analysis_report(task_id: str) -> AnalysisReport:
    """Get the completed analysis report."""
    if task_id not in _reports:
        if task_id not in _tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        raise HTTPException(status_code=400, detail="Analysis not yet completed")

    return _reports[task_id]


@router.get("/list", response_model=list[dict[str, Any]])
async def list_analyses(limit: int = 20) -> list[dict[str, Any]]:
    """List recent analysis tasks."""
    tasks = []
    for task_id, status in sorted(
        _tasks.items(),
        key=lambda x: x[1].created_at,
        reverse=True,
    )[:limit]:
        tasks.append({
            "task_id": task_id,
            "status": status.status.value,
            "progress": status.progress,
            "created_at": status.created_at.isoformat(),
        })
    return tasks


@router.delete("/{task_id}")
async def cancel_analysis(task_id: str) -> dict[str, str]:
    """Cancel a running analysis task."""
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    status = _tasks[task_id]
    if status.status == AnalysisStatusEnum.RUNNING:
        # In a real implementation, you'd signal the background task to stop
        status.status = AnalysisStatusEnum.FAILED
        status.updated_at = datetime.now()
        return {"message": "Analysis cancelled"}
    elif status.status == AnalysisStatusEnum.COMPLETED:
        raise HTTPException(status_code=400, detail="Cannot cancel completed analysis")
    else:
        status.status = AnalysisStatusEnum.FAILED
        status.updated_at = datetime.now()
        return {"message": "Analysis cancelled"}
