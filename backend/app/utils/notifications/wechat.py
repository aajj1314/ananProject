"""WeChat notification channel adapter."""

import logging
from typing import Any

from app.config import get_settings
from app.utils.notifications.base import NotificationChannel

logger = logging.getLogger(__name__)


class WeChatChannel(NotificationChannel):
    """WeChat Official Account/Miniprogram notification delivery."""

    channel_name = "wechat"

    def __init__(self) -> None:
        settings = get_settings()
        self.wechat_app_id = settings.wechat_app_id
        self.wechat_app_secret = settings.wechat_app_secret
        self.wechat_template_id = settings.wechat_template_id

    async def send(
        self,
        recipient: str,
        title: str,
        content: str,
        **kwargs: Any,
    ) -> tuple[bool, str]:
        """Send WeChat template message notification."""
        if not await self.is_available():
            return False, "WeChat channel not configured"

        # Dummy implementation - add real WeChat API calls here
        logger.info(
            f"[DUMMY WECHAT] To: {recipient}, Title: {title}, Content: {content}, "
            f"Template: {self.wechat_template_id}"
        )
        return True, "delivered (dummy)"

    async def is_available(self) -> bool:
        """Check if WeChat is configured."""
        return bool(self.wechat_app_id and self.wechat_app_secret and self.wechat_template_id)
