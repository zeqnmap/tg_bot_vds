import logging
from html import escape

from aiogram import F, Router

from aiogram.exceptions import TelegramBadRequest, TelegramAPIError
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.application.services.request_service import RequestService
from app.domain.models import RequestType, UserRequest
from app.domain.validators import is_valid_full_name, normalize_full_name
from app.infrastructure.telegram.keyboards import request_type_keyboard
from app.infrastructure.telegram.states import RequestForm


def build_router(request_service: RequestService) -> Router:
    router = Router(name="request_flow")

    @router.message(CommandStart())
    async def start_handler(message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer("Здравствуйте! Что вы хотите сделать?", reply_markup=request_type_keyboard())

    @router.callback_query(F.data.startswith("request:"))
    async def request_type_handler(callback: CallbackQuery, state: FSMContext) -> None:
        selected = callback.data.removeprefix("request:") if callback.data else ""
        try:
            request_type = RequestType(selected)
        except ValueError:
            await callback.answer("Неизвестный вариант", show_alert=True)
            return

        await state.update_data(request_type=request_type.value)
        await state.set_state(RequestForm.waiting_for_full_name)
        if callback.message:
            await _safe_delete(callback.message)
            prompt = await callback.message.answer(
                "Введите ваше ФИО.\nНапример: <i>Иванов Иван Иванович</i>"
            )
            await state.update_data(prompt_id=prompt.message_id)
        await callback.answer()

    @router.message(RequestForm.waiting_for_full_name)
    async def full_name_handler(message: Message, state: FSMContext) -> None:
        value = normalize_full_name(message.text or "")
        if not is_valid_full_name(value):
            await message.answer(
                "Не удалось распознать ФИО. Введите его буквами, например:\n"
                "<i>Иванов Иван Иванович</i>"
            )
            return

        data = await state.get_data()
        await state.update_data(full_name=value)
        await state.set_state(RequestForm.waiting_for_description)
        await _delete_prompt(message, data.get("prompt_id"))
        await _safe_delete(message)
        if RequestType(data["request_type"]) == RequestType.IDEA:
            text = "Опишите вашу идею 💡"
        else:
            text = "Расскажите, что вы хотели бы обсудить на встрече, или напишите ваши вопросы."
        prompt = await message.answer(text)
        await state.update_data(prompt_id=prompt.message_id)

    @router.message(RequestForm.waiting_for_description)
    async def description_handler(message: Message, state: FSMContext) -> None:
        if message.text is None:
            await message.answer("Пожалуйста, отправьте описание текстом.")
            return

        data = await state.get_data()
        request = UserRequest(
            full_name=data["full_name"],
            request_type=RequestType(data["request_type"]),
            telegram_user_id=message.from_user.id,
            description=message.text,
            telegram_username=message.from_user.username,
        )
        try:
            await request_service.submit(request)
        except (TelegramAPIError, RuntimeError):
            logging.getLogger(__name__).exception("Could not deliver request")
            await message.answer("Не удалось отправить заявку. Попробуйте отправить описание ещё раз позже.")
            return
        await state.clear()
        await _delete_prompt(message, data.get("prompt_id"))
        await _safe_delete(message)
        await message.answer(
            "✅ <b>Заявка собрана</b>\n\n"
            f"<b>ФИО:</b> {escape(request.full_name)}\n"
            f"<b>Вы выбрали:</b> {request.request_type.label}\n\n"
            "Спасибо! Ваше описание и заявка отправлены администраторам."
        )

    @router.message()
    async def fallback_handler(message: Message) -> None:
        await message.answer("Нажмите /start, чтобы создать заявку.")

    return router


async def _delete_prompt(message: Message, prompt_id: int | None) -> None:
    if prompt_id is not None:
        try:
            await message.bot.delete_message(message.chat.id, prompt_id)
        except TelegramBadRequest:
            pass


async def _safe_delete(message: Message) -> None:
    try:
        await message.delete()
    except TelegramBadRequest:
        pass
