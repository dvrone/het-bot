from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from bot.fsm.states import EditProfileState
from bot.keyboards.inline import (districts_keyboard, profile_keyboard,
                                  regions_keyboard)
from bot.keyboards.reply import phone_keyboard
from bot.services.db import get_user, get_user_lang
from bot.utils.phone import normalize_phone
from core.database import SessionLocal
from core.texts import t

router = Router()


async def show_profile(message: Message, lang: str, user) -> None:
    user_type_label = t(lang, f"type_{user.user_type or 'individual'}")
    text = (
        f"👤 <b>{t(lang, 'profile_title')}</b>\n\n"
        f"🧑 {t(lang, 'profile_name')}: {user.name or '—'}\n"
        f"🏢 {t(lang, 'profile_type')}: {user_type_label}\n"
        f"📞 {t(lang, 'profile_phone')}: {user.phone_no or '—'}\n"
        f"📍 {t(lang, 'profile_region')}: {user.region or '—'}\n"
        f"🏘 {t(lang, 'profile_district')}: {user.district or '—'}\n"
        f"🏠 {t(lang, 'profile_address')}: {user.address_detail or '—'}\n"
        f"🔢 {t(lang, 'profile_account_number')}: {user.account_number or '—'}"
    )
    await message.answer(text, reply_markup=profile_keyboard(lang))


@router.message(Command("profile"))
async def cmd_profile(message: Message, state: FSMContext) -> None:
    await state.clear()
    async with SessionLocal() as session:
        user = await get_user(session, message.from_user.id)
        if not user or not user.is_registered:
            lang = await get_user_lang(session, message.from_user.id)
            await message.answer(t(lang, "not_registered"))
            return
        lang = user.lang_code or "uz"
        await show_profile(message, lang, user)


@router.callback_query(F.data.startswith("edit:"))
async def cb_edit_field(call: CallbackQuery, state: FSMContext) -> None:
    field = call.data.split(":")[1]
    async with SessionLocal() as session:
        lang = await get_user_lang(session, call.from_user.id)

    await state.update_data(edit_field=field)

    if field == "name":
        await call.message.answer(t(lang, "ask_name"))
        await state.set_state(EditProfileState.editing_name)
    elif field == "phone":
        await call.message.answer(
            t(lang, "ask_phone"), reply_markup=phone_keyboard(lang)
        )
        await state.set_state(EditProfileState.editing_phone)
    elif field == "region":
        await call.message.answer(
            t(lang, "ask_region"), reply_markup=regions_keyboard(lang)
        )
        await state.set_state(EditProfileState.editing_region)
    elif field == "district":
        await call.message.answer(
            t(lang, "ask_district"), reply_markup=districts_keyboard(lang)
        )
        await state.set_state(EditProfileState.editing_district)
    elif field == "address":
        await call.message.answer(t(lang, "ask_address_detail"))
        await state.set_state(EditProfileState.editing_address)
    elif field == "account_number":
        await call.message.answer(t(lang, "ask_account_number"))
        await state.set_state(EditProfileState.editing_account_number)
    await call.answer()


@router.message(EditProfileState.editing_name, F.text)
async def edit_name(message: Message, state: FSMContext) -> None:
    async with SessionLocal() as session:
        lang = await get_user_lang(session, message.from_user.id)
        user = await get_user(session, message.from_user.id)
        if user:
            user.name = message.text.strip()
            await session.commit()
            await session.refresh(user)
            await state.clear()
            await message.answer(t(lang, "profile_updated"))
            await show_profile(message, lang, user)


@router.message(EditProfileState.editing_phone, F.contact)
async def edit_phone_contact(message: Message, state: FSMContext) -> None:
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = f"+{phone}"
    async with SessionLocal() as session:
        lang = await get_user_lang(session, message.from_user.id)
        user = await get_user(session, message.from_user.id)
        if user:
            user.phone_no = phone
            await session.commit()
            await session.refresh(user)
            await state.clear()
            await message.answer(
                t(lang, "profile_updated"), reply_markup=ReplyKeyboardRemove()
            )
            await show_profile(message, lang, user)


@router.message(EditProfileState.editing_phone, F.text)
async def edit_phone_text(message: Message, state: FSMContext) -> None:
    async with SessionLocal() as session:
        lang = await get_user_lang(session, message.from_user.id)
    phone = normalize_phone(message.text.strip())
    if not phone:
        await message.answer(t(lang, "invalid_phone"))
        return
    async with SessionLocal() as session:
        user = await get_user(session, message.from_user.id)
        if user:
            user.phone_no = phone
            await session.commit()
            await session.refresh(user)
            await state.clear()
            await message.answer(
                t(lang, "profile_updated"), reply_markup=ReplyKeyboardRemove()
            )
            await show_profile(message, lang, user)


@router.callback_query(EditProfileState.editing_region, F.data.startswith("region:"))
async def edit_region(call: CallbackQuery, state: FSMContext) -> None:
    region = call.data[len("region:") :]
    async with SessionLocal() as session:
        lang = await get_user_lang(session, call.from_user.id)
        user = await get_user(session, call.from_user.id)
        if user:
            user.region = region
            await session.commit()
            await session.refresh(user)
            await state.clear()
            await call.message.answer(t(lang, "profile_updated"))
            await show_profile(call.message, lang, user)
    await call.answer()


@router.callback_query(
    EditProfileState.editing_district, F.data.startswith("district:")
)
async def edit_district(call: CallbackQuery, state: FSMContext) -> None:
    district = call.data[len("district:") :]
    async with SessionLocal() as session:
        lang = await get_user_lang(session, call.from_user.id)
        user = await get_user(session, call.from_user.id)
        if user:
            user.district = district
            await session.commit()
            await session.refresh(user)
            await state.clear()
            await call.message.answer(t(lang, "profile_updated"))
            await show_profile(call.message, lang, user)
    await call.answer()


@router.message(EditProfileState.editing_address, F.text)
async def edit_address(message: Message, state: FSMContext) -> None:
    async with SessionLocal() as session:
        lang = await get_user_lang(session, message.from_user.id)
        user = await get_user(session, message.from_user.id)
        if user:
            user.address_detail = message.text.strip()
            await session.commit()
            await session.refresh(user)
            await state.clear()
            await message.answer(t(lang, "profile_updated"))
            await show_profile(message, lang, user)


@router.message(EditProfileState.editing_account_number, F.text)
async def edit_account_number(message: Message, state: FSMContext) -> None:
    async with SessionLocal() as session:
        lang = await get_user_lang(session, message.from_user.id)
        user = await get_user(session, message.from_user.id)
        if user:
            user.account_number = message.text.strip()
            await session.commit()
            await session.refresh(user)
            await state.clear()
            await message.answer(t(lang, "profile_updated"))
            await show_profile(message, lang, user)
