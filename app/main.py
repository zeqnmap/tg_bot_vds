import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, MenuButtonCommands

from app.application.services.request_service import RequestService
from app.config.settings import Settings
from app.infrastructure.telegram.handlers import build_router
from app.infrastructure.telegram.notifications import TelegramNotifier


def create_dispatcher(settings: Settings, bot: Bot) -> Dispatcher:
    dispatcher = Dispatcher()
    notifier = TelegramNotifier(bot)
    service = RequestService(notifier=notifier, admin_chat_ids=settings.admin_chat_ids)
    dispatcher.include_router(build_router(service))
    return dispatcher


async def main() -> None:
    settings = Settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    if not settings.admin_chat_ids:
        logging.getLogger(__name__).warning(
            "ADMIN_CHAT_IDS is empty: applications will not be delivered to admins."
        )

    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = create_dispatcher(settings, bot)
    try:
        await bot.set_my_commands([BotCommand(command="start", description="Начать заново")])
        await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
        await bot.delete_webhook(drop_pending_updates=True)
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
