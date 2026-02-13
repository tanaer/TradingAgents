"""WebSocket router for real-time updates."""

import asyncio
import json
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, task_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        self.active_connections[task_id].append(websocket)

    def disconnect(self, websocket: WebSocket, task_id: str):
        """Remove a WebSocket connection."""
        if task_id in self.active_connections:
            if websocket in self.active_connections[task_id]:
                self.active_connections[task_id].remove(websocket)
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]

    async def broadcast(self, task_id: str, message: dict):
        """Broadcast a message to all connections for a task."""
        if task_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[task_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_connections.append(connection)

            # Clean up dead connections
            for conn in dead_connections:
                self.disconnect(conn, task_id)


manager = ConnectionManager()


@router.websocket("/analysis/{task_id}")
async def websocket_analysis(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for real-time analysis updates."""
    await manager.connect(websocket, task_id)

    try:
        while True:
            # Wait for client messages (ping/pong or commands)
            data = await websocket.receive_text()

            # Handle commands
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        manager.disconnect(websocket, task_id)


async def push_analysis_update(task_id: str, event_type: str, data: dict):
    """Push an analysis update to all connected clients."""
    message = {
        "type": event_type,
        "task_id": task_id,
        "timestamp": datetime.now().isoformat(),
        **data,
    }
    await manager.broadcast(task_id, message)


async def push_agent_status(task_id: str, agent_name: str, status: str, progress: float, message: str = ""):
    """Push agent status update."""
    await push_analysis_update(task_id, "agent_status", {
        "agent": agent_name,
        "status": status,
        "progress": progress,
        "message": message,
    })


async def push_report_chunk(task_id: str, chunk: str):
    """Push a chunk of the report."""
    await push_analysis_update(task_id, "report_chunk", {
        "content": chunk,
    })


async def push_completion(task_id: str, success: bool, message: str = ""):
    """Push completion notification."""
    await push_analysis_update(task_id, "completed", {
        "success": success,
        "message": message,
    })
