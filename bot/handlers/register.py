from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from bot.fsm.states import RegisterState
from bot.keyboards.inline import (districts_keyboard, regions_keyboard,
                                  type_keyboard)
from bot.keyboards.reply import phone_keyboard
from bot.services.db import get_user, get_user_lang
from bot.utils.phone import normalize_phone
from core.database import SessionLocal
from core.texts import t

router = Router()


@router.message(RegisterState.asking_name, F.text)
async def ask_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if len(name.split()) < 2:
        async with SessionLocal() as session:
            lang = await get_user_lang(session, message.from_user.id)
        await message.answer(t(lang, "invalid_name"))
        return
    async with SessionLocal() as session:
        lang = await get_user_lang(session, message.from_user.id)
        user = await get_user(session, message.from_user.id)
        if user:
            user.name = name
            await session.commit()
    await state.update_data(name=name)
    await message.answer(
        t(lang, "ask_type", name=name), reply_markup=type_keyboard(lang)
    )
    await state.set_state(RegisterState.asking_type)


@router.callback_query(RegisterState.asking_type, F.data.startswith("type:"))
async def cb_type(call: CallbackQuery, state: FSMContext) -> None:
    user_type = call.data.split(":")[1]
    async with SessionLocal() as session:
        lang = await get_user_lang(session, call.from_user.id)
        user = await get_user(session, call.from_user.id)
        if user:
            user.user_type = user_type
            await session.commit()
    await state.update_data(user_type=user_type)
    await call.message.delete()
    if user_type == "legal":
        await call.message.answer(t(lang, "ask_company"))
        await state.set_state(RegisterState.asking_company)
    else:
        await call.message.answer(
            t(lang, "ask_phone"), reply_markup=phone_keyboard(lang)
        )
        await state.set_state(RegisterState.asking_phone)
    await call.answer()


@router.message(RegisterState.asking_company, F.text)
async def ask_company(message: Message, state: FSMContext) -> None:
    company_name = message.text.strip()
    async with SessionLocal() as session:
        lang = await get_user_lang(session, message.from_user.id)
        user = await get_user(session, message.from_user.id)
        if user:
            user.company_name = company_name
            await session.commit()
    await state.update_data(company_name=company_name)
    await message.answer(t(lang, "ask_phone"), reply_markup=phone_keyboard(lang))
    await state.set_state(RegisterState.asking_phone)


@router.message(RegisterState.asking_phone, F.contact)
async def ask_phone_contact(message: Message, state: FSMContext) -> None:
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = f"+{phone}"
    async with SessionLocal() as session:
        lang = await get_user_lang(session, message.from_user.id)
        user = await get_user(session, message.from_user.id)
        if user:
            user.phone_no = phone
            await session.commit()
    await state.update_data(phone=phone)
    await message.answer("✅", reply_markup=ReplyKeyboardRemove())
    await message.answer(t(lang, "ask_region"), reply_markup=regions_keyboard(lang))
    await state.set_state(RegisterState.asking_region)


@router.message(RegisterState.asking_phone, F.text)
async def ask_phone_text(message: Message, state: FSMContext) -> None:
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
    await state.update_data(phone=phone)
    await message.answer("✅", reply_markup=ReplyKeyboardRemove())
    await message.answer(t(lang, "ask_region"), reply_markup=regions_keyboard(lang))
    await state.set_state(RegisterState.asking_region)


@router.callback_query(RegisterState.asking_region, F.data.startswith("region:"))
async def cb_region(call: CallbackQuery, state: FSMContext) -> None:
    region = call.data[len("region:") :]
    async with SessionLocal() as session:
        lang = await get_user_lang(session, call.from_user.id)
        user = await get_user(session, call.from_user.id)
        if user:
            user.region = region
            await session.commit()
    await state.update_data(region=region)
    await call.message.edit_text(
        f"✅ {region}\n\n{t(lang, 'ask_district')}",
        reply_markup=districts_keyboard(lang),
    )
    await state.set_state(RegisterState.asking_district)
    await call.answer()


@router.callback_query(RegisterState.asking_district, F.data.startswith("district:"))
async def cb_district(call: CallbackQuery, state: FSMContext) -> None:
    district = call.data[len("district:") :]
    async with SessionLocal() as session:
        lang = await get_user_lang(session, call.from_user.id)
        user = await get_user(session, call.from_user.id)
        if user:
            user.district = district
            await session.commit()
    await state.update_data(district=district)
    await call.message.edit_text(f"✅ {district}")
    await call.message.answer(t(lang, "ask_address_detail"))
    await state.set_state(RegisterState.asking_address_detail)
    await call.answer()


@router.message(RegisterState.asking_address_detail, F.text)
async def ask_address_detail(message: Message, state: FSMContext) -> None:
    address_detail = message.text.strip()
    async with SessionLocal() as session:
        lang = await get_user_lang(session, message.from_user.id)
        user = await get_user(session, message.from_user.id)
        if user:
            user.address_detail = address_detail
            await session.commit()
    await state.update_data(address_detail=address_detail)
    await message.answer(t(lang, "ask_account_number"))
    await state.set_state(RegisterState.asking_account_number)


@router.message(RegisterState.asking_account_number, F.text)
async def ask_account_number(message: Message, state: FSMContext) -> None:
    account_number = message.text.strip()
    async with SessionLocal() as session:
        lang = await get_user_lang(session, message.from_user.id)
        user = await get_user(session, message.from_user.id)
        user_type = user.user_type if user else "individual"
    from bot.utils.validators import validate_account_number

    if not validate_account_number(account_number, user_type):
        await message.answer(t(lang, "invalid_account_number"))
        return
    async with SessionLocal() as session:
        user = await get_user(session, message.from_user.id)
        if user:
            user.account_number = account_number
            user.is_registered = True
            await session.commit()
            await session.refresh(user)
            user_type_label = t(lang, f"type_{user.user_type or 'individual'}")
            name = user.name or ""
            phone = user.phone_no or ""
            region = user.region or ""
            district = user.district or ""
            address_detail = user.address_detail or ""
    await state.clear()
    await message.answer(
        t(
            lang,
            "registered_ok",
            name=name,
            user_type=user_type_label,
            phone=phone,
            region=region,
            district=district,
            address_detail=address_detail,
        )
    )
