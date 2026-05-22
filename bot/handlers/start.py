from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.fsm.states import LangState, RegisterState
from bot.keyboards.inline import lang_keyboard
from bot.services.db import get_or_create_user
from core.database import SessionLocal
from core.texts import TEXTS, t

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    async with SessionLocal() as session:
        user = await get_or_create_user(
            session, message.from_user.id, message.from_user.username
        )
        if user.is_registered:
            await message.answer(t(user.lang_code or "uz", "already_registered"))
            return
    await message.answer(
        f"{TEXTS['kaa']['welcome_company']}\n\n{TEXTS['kaa']['choose_lang']}",
        reply_markup=lang_keyboard(),
    )
    await state.set_state(LangState.choosing)


@router.callback_query(LangState.choosing, F.data.startswith("lang:"))
async def cb_lang(call: CallbackQuery, state: FSMContext) -> None:
    lang = call.data.split(":")[1]
    async with SessionLocal() as session:
        user = await get_or_create_user(
            session, call.from_user.id, call.from_user.username
        )
        user.lang_code = lang
        await session.commit()
    await call.message.edit_text(
        t(lang, "welcome_company") + "\n\n" + t(lang, "ask_name")
    )
    await state.set_state(RegisterState.asking_name)
    await call.answer()
