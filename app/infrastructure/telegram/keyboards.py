from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.domain.models import RequestType


def request_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=RequestType.IDEA.label, callback_data="request:idea")],
            [InlineKeyboardButton(text=RequestType.TOP_MEETING.label, callback_data="request:top_meeting")],
        ]
    )
