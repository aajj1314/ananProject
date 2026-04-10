"""SMS notification channel adapter."""

import logging
from typing import Any

from app.config import get_settings
from app.utils.notifications.base import NotificationChannel

logger = logging.getLogger(__name__)


class SMSChannel(NotificationChannel):
    """SMS notification delivery via configurable provider."""

    channel_name = "sms"

    def __init__(self) -> None:
        settings = get_settings()
        self.sms_provider = settings.sms_provider or "dummy"
        self.sms_api_key = settings.sms_api_key
        self.sms_api_secret = settings.sms_api_secret
        self.sms_from_number = settings.sms_from_number

    async def send(
        self,
        recipient: str,
        title: str,
        content: str,
        **kwargs: Any,
    ) -> tuple[bool, str]:
        """Send SMS notification."""
        if not await self.is_available():
            return False, "SMS channel not configured"

        if self.sms_provider == "dummy":
            logger.info(f"[DUMMY SMS] To: {recipient}, Title: {title}, Content: {content}")
            return True, "delivered (dummy)"

        # Add real provider implementations here (e.g., Aliyun, Tencent Cloud)
        # if self.sms_provider == "aliyun":
        #     return await self._send_aliyun(recipient, title, content)

        return False, f"Unsupported SMS provider: {self.sms_provider}"

    async def is_available(self) -> bool:
        """Check if SMS is configured."""
        if self.sms_provider == "dummy":
            return True
        return bool(self.sms_api_key and self.sms_from_number)
