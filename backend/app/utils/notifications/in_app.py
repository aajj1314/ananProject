"""In-app notification channel adapter."""

from typing import Any

from app.utils.notifications.base import NotificationChannel


class InAppChannel(NotificationChannel):
    """Simple in-app notification channel (always available)."""

    channel_name = "in_app"

    async def send(
        self,
        recipient: str,
        title: str,
        content: str,
        **kwargs: Any,
    ) -> tuple[bool, str]:
        """In-app notifications are just stored, no delivery needed."""
        return True, "stored"

    async def is_available(self) -> bool:
        """In-app is always available."""
        return True
