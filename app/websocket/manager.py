"""
Sanos y Salvos — WebSocket Connection Manager
Manages real-time WebSocket connections for push notifications.
"""

import json
import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger("ws.manager")


class ConnectionManager:
    """
    Manages active WebSocket connections.
    Users connect via /ws/notifications/{user_id} to receive real-time alerts.
    """

    def __init__(self):
        # user_id -> list of active connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Global broadcast connections (for dashboard)
        self.broadcast_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, user_id: str = None):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        if user_id:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
            logger.info(f"🔌 User {user_id} connected via WebSocket")
        else:
            self.broadcast_connections.append(websocket)
            logger.info("🔌 Broadcast listener connected")

    def disconnect(self, websocket: WebSocket, user_id: str = None):
        """Remove a WebSocket connection."""
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            logger.info(f"🔌 User {user_id} disconnected")
        elif websocket in self.broadcast_connections:
            self.broadcast_connections.remove(websocket)

    async def send_to_user(self, user_id: str, message: dict):
        """Send a notification to a specific user."""
        if user_id in self.active_connections:
            for ws in self.active_connections[user_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    self.disconnect(ws, user_id)

    async def broadcast(self, message: dict):
        """Broadcast a notification to all connected clients."""
        disconnected = []
        for ws in self.broadcast_connections:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)

        for ws in disconnected:
            self.broadcast_connections.remove(ws)

        # Also send to all individual user connections
        for user_id, connections in self.active_connections.items():
            for ws in connections:
                try:
                    await ws.send_json(message)
                except Exception:
                    pass

    def get_connected_users(self) -> list:
        """Get list of connected user IDs."""
        return list(self.active_connections.keys())


# Singleton manager
manager = ConnectionManager()
