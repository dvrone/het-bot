from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from core.texts import t


def phone_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "btn_share_phone"), request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
