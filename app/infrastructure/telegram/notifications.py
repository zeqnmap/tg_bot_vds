from aiogram import Bot
from aiogram.utils.markdown import hcode
from html import escape

from app.domain.models import UserRequest


class TelegramNotifier:
    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    async def notify(self, request: UserRequest, chat_ids: list[int]) -> None:
        username = f"@{request.telegram_username}" if request.telegram_username else "не указан"
        text = (
            "📩 <b>Новая заявка</b>\n\n"
            f"<b>ФИО:</b> {escape(request.full_name)}\n"
            f"<b>Тип:</b> {request.request_type.label}\n"
            f"<b>Username:</b> {hcode(username)}\n"
            f"<b>ID пользователя:</b> <code>{request.telegram_user_id}</code>\n\n"
            "<b>Описание:</b>\n"
        )
        pages = _split_description(request.description)
        for chat_id in chat_ids:
            await self._bot.send_message(chat_id=chat_id, text=text + pages[0])
            for page in pages[1:]:
                await self._bot.send_message(chat_id=chat_id, text=page)


def _split_description(description: str) -> list[str]:
    """Escape HTML and keep each message within Telegram's length limit."""
    pages: list[str] = []
    current: list[str] = []
    length = 0
    for char in description:
        escaped = escape(char)
        if length + len(escaped) > 2500:
            pages.append("".join(current))
            current = []
            length = 0
        current.append(escaped)
        length += len(escaped)
    pages.append("".join(current))
    return pages
