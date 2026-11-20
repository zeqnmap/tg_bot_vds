import html
import unittest

from app.domain.models import RequestType, UserRequest
from app.infrastructure.telegram.notifications import TelegramNotifier


class FakeBot:
    def __init__(self) -> None:
        self.messages = []

    async def send_message(self, chat_id: int, text: str) -> None:
        self.messages.append((chat_id, text))


class PartiallyFailingBot(FakeBot):
    async def send_message(self, chat_id: int, text: str) -> None:
        if chat_id == -1002:
            from aiogram.exceptions import TelegramBadRequest

            raise TelegramBadRequest(method="sendMessage", message="chat not found")
        await super().send_message(chat_id, text)


class NotificationTests(unittest.IsolatedAsyncioTestCase):
    async def test_description_is_escaped_and_delivered_in_full(self) -> None:
        bot = FakeBot()
        description = "Вопрос 123 <важно> & ответ.\n" * 200
        request = UserRequest(
            full_name="Иванов Иван",
            request_type=RequestType.TOP_MEETING,
            telegram_user_id=123,
            description=description,
        )
        await TelegramNotifier(bot).notify(request, [-1001])
        self.assertTrue(all(chat_id == -1001 and len(text) <= 4096 for chat_id, text in bot.messages))
        sent = bot.messages[0][1].split("<b>Описание:</b>\n", 1)[1]
        sent += "".join(text for _, text in bot.messages[1:])
        self.assertEqual(html.unescape(sent), description)

    async def test_one_bad_admin_chat_does_not_block_good_chat(self) -> None:
        bot = PartiallyFailingBot()
        request = UserRequest(
            full_name="Иванов Иван",
            request_type=RequestType.IDEA,
            telegram_user_id=123,
            description="Идея",
        )
        await TelegramNotifier(bot).notify(request, [-1001, -1002])
        self.assertEqual([chat_id for chat_id, _ in bot.messages], [-1001])


if __name__ == "__main__":
    unittest.main()
