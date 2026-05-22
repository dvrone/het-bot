from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import func, select

from bot.fsm.states import AdminReplyState
from bot.keyboards.inline import reply_keyboard, requests_filter_keyboard
from bot.models.user import Request, User
from bot.services.notify import safe_send
from core.config import ADMIN_IDS
from core.database import SessionLocal
from core.texts import REQUEST_TYPES, t

router = Router()


def get_category_label(lang: str, category_id: str) -> str:
    categories = REQUEST_TYPES.get(lang, REQUEST_TYPES["uz"])
    cat = next((c for c in categories if c["id"] == category_id), None)
    return cat["label"] if cat else category_id


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if message.from_user.id not in ADMIN_IDS:
        return
    async with SessionLocal() as session:
        users_count = (
            (await session.execute(select(User).where(User.is_registered == True)))
            .scalars()
            .all()
        )
        requests_count = (await session.execute(select(Request))).scalars().all()
    await message.answer(
        "🛠 <b>Admin Panel</b>\n\n"
        f"👥 Ro'yxatdan o'tganlar: <b>{len(users_count)}</b>\n"
        f"📨 Jami arizalar: <b>{len(requests_count)}</b>",
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("users"))
async def cmd_users(message: Message) -> None:
    if message.from_user.id not in ADMIN_IDS:
        return
    async with SessionLocal() as session:
        users = (
            (await session.execute(select(User).where(User.is_registered == True)))
            .scalars()
            .all()
        )
    if not users:
        await message.answer("No registered users yet.")
        return
    lines = ["<b>Registered Users:</b>\n"]
    for u in users[:20]:
        lines.append(
            f"• {u.name or '—'} | @{u.username or '—'} | {u.phone_no or '—'} | "
            f"{u.user_type or '—'} | 🔢 {u.account_number or '—'} | <code>{u.telegram_id}</code>"
        )
    await message.answer("\n".join(lines), parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith("reply:"))
async def cb_admin_reply(call: CallbackQuery, state: FSMContext) -> None:
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("❌ Access denied", show_alert=True)
        return
    request_id = int(call.data.split(":")[1])
    await state.update_data(reply_request_id=request_id)
    await call.message.answer("✏️ Javob matnini kiriting:\n✏️ Введите текст ответа:")
    await state.set_state(AdminReplyState.waiting_text)
    await call.answer()


@router.message(AdminReplyState.waiting_text, F.text)
async def admin_send_reply(message: Message, state: FSMContext, bot) -> None:
    if message.from_user.id not in ADMIN_IDS:
        await state.clear()
        return
    reply_text = message.text.strip()
    data = await state.get_data()
    request_id = data.get("reply_request_id")

    async with SessionLocal() as session:
        req = await session.get(Request, request_id)
        if not req:
            await message.answer("❌ Request not found.")
            await state.clear()
            return
        user = await session.get(User, req.user_id)
        if not user:
            await message.answer("❌ User not found.")
            await state.clear()
            return
        lang = user.lang_code or "uz"
        user_tg_id = user.telegram_id
        req.is_replied = True
        await session.commit()

    success = await safe_send(
        bot,
        user_tg_id,
        t(lang, "admin_reply_header", text=reply_text),
        parse_mode=ParseMode.HTML,
    )
    if success:
        await message.answer("✅ Javob yuborildi. / ✅ Ответ otправлен.")
    else:
        await message.answer(
            f"❌ Javob yuborib bo'lmadi (foydalanuvchi botni bloklagan).\n"
            f"❌ Не удалось отправить ответ (бот заблокирован).\n"
            f"User ID: {user_tg_id}"
        )
    await state.clear()


REQUESTS_PAGE_SIZE = 10


async def build_requests_text(
    session, status_filter: str, page: int
) -> tuple[str, int]:
    query = select(Request)
    if status_filter == "pending":
        query = query.where(Request.is_replied == False)
    elif status_filter == "replied":
        query = query.where(Request.is_replied == True)

    count_result = await session.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar() or 0
    total_pages = max(1, (total + REQUESTS_PAGE_SIZE - 1) // REQUESTS_PAGE_SIZE)

    query = query.order_by(Request.created_at.desc())
    query = query.offset(page * REQUESTS_PAGE_SIZE).limit(REQUESTS_PAGE_SIZE)
    requests = (await session.execute(query)).scalars().all()

    if not requests:
        return "📋 Arizalar yo'q.", total_pages

    lines = [f"📋 <b>Arizalar</b> — jami: {total}\n"]
    for req in requests:
        user = await session.get(User, req.user_id)
        lang = user.lang_code or "uz" if user else "uz"
        status = "✅" if req.is_replied else "🕐"
        name = user.name or "—" if user else "—"
        date = req.created_at.strftime("%d.%m.%Y %H:%M")
        cat = get_category_label(lang, req.request_category or "")
        lines.append(
            f"{status} <b>{name}</b> | {cat}\n"
            f"    {req.message_text[:60]}{'...' if len(req.message_text) > 60 else ''}\n"
            f"    🕓 {date}\n"
        )
    return "\n".join(lines), total_pages


@router.message(Command("requests"))
async def cmd_requests(message: Message) -> None:
    if message.from_user.id not in ADMIN_IDS:
        return
    async with SessionLocal() as session:
        text, total_pages = await build_requests_text(session, "all", 0)
    await message.answer(
        text,
        reply_markup=requests_filter_keyboard("all", 0, total_pages),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("rfilter:"))
async def cb_requests_filter(call: CallbackQuery) -> None:
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("❌ Access denied", show_alert=True)
        return
    _, status_filter, page_str = call.data.split(":")
    page = int(page_str)
    async with SessionLocal() as session:
        text, total_pages = await build_requests_text(session, status_filter, page)
    await call.message.edit_text(
        text,
        reply_markup=requests_filter_keyboard(status_filter, page, total_pages),
        parse_mode=ParseMode.HTML,
    )
    await call.answer()


@router.callback_query(F.data == "noop")
async def cb_noop(call: CallbackQuery) -> None:
    await call.answer()
