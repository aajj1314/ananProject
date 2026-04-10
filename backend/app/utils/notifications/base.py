"""Base notification channel adapter."""

from abc import ABC, abstractmethod
from typing import Any


class NotificationChannel(ABC):
    """Abstract base for notification delivery channels."""

    channel_name: str

    @abstractmethod
    async def send(
        self,
        recipient: str,
        title: str,
        content: str,
        **kwargs: Any,
    ) -> tuple[bool, str]:
        """
        Send a notification via this channel.

        Returns:
            (success: bool, status_message: str)
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if this channel is configured and available."""
        pass
