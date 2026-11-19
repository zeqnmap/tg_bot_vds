import logging
from typing import Protocol

from app.domain.models import UserRequest

logger = logging.getLogger(__name__)


class RequestNotifier(Protocol):
    async def notify(self, request: UserRequest, chat_ids: list[int]) -> None: ...


class RequestService:
    def __init__(self, notifier: RequestNotifier, admin_chat_ids: list[int]) -> None:
        self._notifier = notifier
        self._admin_chat_ids = admin_chat_ids

    async def submit(self, request: UserRequest) -> None:
        if not self._admin_chat_ids:
            raise RuntimeError("ADMIN_CHAT_IDS is empty")
        await self._notifier.notify(request, self._admin_chat_ids)
