"""Notification channel registry and router."""

import logging
from typing import Any

from app.config import get_settings
from app.utils.notifications.base import NotificationChannel
from app.utils.notifications.in_app import InAppChannel
from app.utils.notifications.sms import SMSChannel
from app.utils.notifications.wechat import WeChatChannel

logger = logging.getLogger(__name__)


class NotificationRouter:
    """Route notifications to configured channels."""

    def __init__(self) -> None:
        self.channels: dict[str, NotificationChannel] = {}
        self._register_default_channels()

    def _register_default_channels(self) -> None:
        """Register built-in notification channels."""
        self.register_channel(InAppChannel())
        self.register_channel(SMSChannel())
        self.register_channel(WeChatChannel())

    def register_channel(self, channel: NotificationChannel) -> None:
        """Register a notification channel."""
        self.channels[channel.channel_name] = channel

    async def send_to_channel(
        self,
        channel_name: str,
        recipient: str,
        title: str,
        content: str,
        **kwargs: Any,
    ) -> tuple[bool, str]:
        """Send a notification to a specific channel."""
        if channel_name not in self.channels:
            return False, f"Unknown channel: {channel_name}"

        channel = self.channels[channel_name]
        if not await channel.is_available():
            return False, f"Channel {channel_name} not available"

        return await channel.send(recipient, title, content, **kwargs)

    async def send_to_all_available(
        self,
        recipient: str,
        title: str,
        content: str,
        channel_allowlist: list[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, tuple[bool, str]]:
        """Send notification to all available channels."""
        settings = get_settings()
        channels = channel_allowlist or settings.notification_channels or ["in_app"]

        results: dict[str, tuple[bool, str]] = {}
        for channel_name in channels:
            if channel_name in self.channels:
                results[channel_name] = await self.send_to_channel(
                    channel_name, recipient, title, content, **kwargs
                )

        return results


# Global notification router instance
_notification_router: NotificationRouter | None = None


def get_notification_router() -> NotificationRouter:
    """Get the global notification router instance."""
    global _notification_router
    if _notification_router is None:
        _notification_router = NotificationRouter()
    return _notification_router
