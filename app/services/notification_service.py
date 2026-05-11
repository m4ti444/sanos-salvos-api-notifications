"""
Sanos y Salvos - Notification Service
Processes match events and generates user notifications.
"""

import logging
from datetime import datetime
from typing import List

from app.websocket.manager import manager

logger = logging.getLogger("notification_service")

# In-memory notification store (for demo; in production use a database)
notifications_store: List[dict] = []


class NotificationService:
    """Handles notification creation and delivery."""

    @staticmethod
    async def create_notification(match_data: dict):
        """
        Create and send notifications when a match is found.
        A dedicated notification is generated per destination user.
        """

        def build_notification(user_id: str, role: str) -> dict:
            return {
                "id": len(notifications_store) + 1,
                "user_id": user_id,
                "type": "match_found",
                "title": "Posible coincidencia encontrada",
                "message": (
                    f"Se detecto una posible coincidencia ({match_data.get('score', 0):.0f}%) "
                    f"para tu reporte {role}."
                ),
                "match_id": match_data.get("_id"),
                "score": match_data.get("score", 0),
                "report_lost_id": match_data.get("report_lost_id"),
                "report_found_id": match_data.get("report_found_id"),
                "pet_lost_name": match_data.get("pet_lost_name", "Desconocido"),
                "pet_found_name": match_data.get("pet_found_name", "Desconocido"),
                "read": False,
                "created_at": datetime.utcnow().isoformat(),
            }

        created = []

        user_lost_id = str(match_data.get("user_lost_id") or "").strip()
        user_found_id = str(match_data.get("user_found_id") or "").strip()

        recipients = []
        if user_lost_id:
            recipients.append((user_lost_id, "perdido"))
        if user_found_id and user_found_id != user_lost_id:
            recipients.append((user_found_id, "encontrado"))

        for user_id, role in recipients:
            notification = build_notification(user_id, role)
            notifications_store.append(notification)
            created.append(notification)
            logger.info(f"Notification created for user {user_id}: {notification['title']}")
            await manager.send_to_user(user_id, notification)

        return created

    @staticmethod
    def get_notifications(user_id: str | None = None, limit: int = 50) -> List[dict]:
        """Get notifications, optionally filtered by user."""
        results = notifications_store
        if user_id:
            results = [n for n in results if str(n.get("user_id")) == str(user_id)]
        results = sorted(results, key=lambda x: x["created_at"], reverse=True)
        return results[:limit]

    @staticmethod
    def mark_as_read(notification_id: int, user_id: str | None = None) -> bool:
        for n in notifications_store:
            if n["id"] == notification_id:
                if user_id and str(n.get("user_id")) != str(user_id):
                    return False
                n["read"] = True
                return True
        return False

    @staticmethod
    def get_unread_count(user_id: str | None = None) -> int:
        if user_id:
            return sum(
                1
                for n in notifications_store
                if not n["read"] and str(n.get("user_id")) == str(user_id)
            )
        return sum(1 for n in notifications_store if not n["read"])
