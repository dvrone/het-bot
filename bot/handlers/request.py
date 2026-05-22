from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.fsm.states import RequestState
from bot.keyboards.inline import (request_categories_keyboard,
                                  request_types_keyboard)
from bot.models.user import Request
from bot.services.db import get_user, get_user_lang
from bot.services.notify import notify_admins
from core.database import SessionLocal
from core.texts import REQUEST_TYPES, t

router = Router()


def get_label(lang: str, category_id: str, type_id: str) -> tuple[str, str]:
    categories = REQUEST_TYPES.get(lang, REQUEST_TYPES["uz"])
    cat = next((c for c in categories if c["id"] == category_id), None)
    cat_label = cat["label"] if cat else category_id
    tp = next((tp for tp in (cat["types"] if cat else []) if tp["id"] == type_id), None)
    type_label = tp["label"] if tp else type_id
    return cat_label, type_label


@router.message(Command("request"))
async def cmd_request(message: Message, state: FSMContext) -> None:
    await state.clear()
    async with SessionLocal() as session:
        user = await get_user(session, message.from_user.id)
        if not user or not user.is_registered:
            lang = await get_user_lang(session, message.from_user.id)
            await message.answer(t(lang, "not_registered"))
            return
        lang = user.lang_code or "uz"
    await message.answer(
        t(lang, "ask_request_category"), reply_markup=request_categories_keyboard(lang)
    )
    await state.set_state(RequestState.choosing_category)


@router.callback_query(RequestState.choosing_category, F.data.startswith("cat:"))
async def cb_category(call: CallbackQuery, state: FSMContext) -> None:
    category_id = call.data.split(":")[1]
    async with SessionLocal() as session:
        lang = await get_user_lang(session, call.from_user.id)

    # Birinchi turni avtomatik tanlash
    from core.texts import REQUEST_TYPES

    categories = REQUEST_TYPES.get(lang, REQUEST_TYPES["uz"])
    cat = next((c for c in categories if c["id"] == category_id), None)
    type_id = cat["types"][0]["id"] if cat and cat["types"] else "other"

    await state.update_data(category_id=category_id, type_id=type_id)
    await call.message.delete()
    await call.message.answer(t(lang, "ask_request"))
    await state.set_state(RequestState.writing)
    await call.answer()


@router.callback_query(RequestState.choosing_type, F.data == "cat:back")
async def cb_back(call: CallbackQuery, state: FSMContext) -> None:
    async with SessionLocal() as session:
        lang = await get_user_lang(session, call.from_user.id)
    await call.message.edit_reply_markup(reply_markup=request_categories_keyboard(lang))
    await state.set_state(RequestState.choosing_category)
    await call.answer()


@router.callback_query(RequestState.choosing_type, F.data.startswith("rtype:"))
async def cb_type(call: CallbackQuery, state: FSMContext) -> None:
    type_id = call.data.split(":")[1]
    async with SessionLocal() as session:
        lang = await get_user_lang(session, call.from_user.id)
    await state.update_data(type_id=type_id)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(t(lang, "ask_request"))
    await state.set_state(RequestState.writing)
    await call.answer()


@router.message(RequestState.writing, F.text)
async def handle_request(message: Message, state: FSMContext, bot) -> None:
    text = message.text.strip()
    data = await state.get_data()
    category_id = data.get("category_id", "")
    type_id = data.get("type_id", "")

    async with SessionLocal() as session:
        user = await get_user(session, message.from_user.id)
        if not user:
            await state.clear()
            return
        lang = user.lang_code or "uz"
        cat_label, type_label = get_label(lang, category_id, type_id)

        req = Request(
            user_id=user.id,
            message_text=text,
            request_category=category_id,
            request_type=type_id,
        )
        session.add(req)
        await session.commit()
        await session.refresh(req)
        request_id = req.id
        user_type_label = t(lang, f"type_{user.user_type or 'individual'}")
        admin_text = t(
            lang,
            "admin_new_request",
            name=user.name or "—",
            user_type=user_type_label,
            company=user.company_name or "—",
            phone=user.phone_no or "—",
            region=user.region or "—",
            district=user.district or "—",
            address=user.address_detail or "—",
            account=user.account_number or "—",
            username=user.username or "no_username",
            tg_id=user.telegram_id,
            text=f"[{cat_label} → {type_label}]\n{text}",
        )
    await message.answer(t(lang, "request_sent"))
    await state.clear()
    await notify_admins(bot, admin_text, request_id, lang, category_id)
