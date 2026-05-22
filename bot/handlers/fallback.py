from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.services.db import get_user_lang
from core.database import SessionLocal
from core.texts import t

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    async with SessionLocal() as session:
        lang = await get_user_lang(session, message.from_user.id)
    await message.answer(t(lang, "help_text"))


@router.message(Command("cancel"), StateFilter("*"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    if await state.get_state() is None:
        return
    async with SessionLocal() as session:
        lang = await get_user_lang(session, message.from_user.id)
    await state.clear()
    await message.answer(t(lang, "cancelled"), reply_markup=ReplyKeyboardRemove())


@router.message()
async def fallback(message: Message) -> None:
    async with SessionLocal() as session:
        lang = await get_user_lang(session, message.from_user.id)
    await message.answer(t(lang, "help_text"))
