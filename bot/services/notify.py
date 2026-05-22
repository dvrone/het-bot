import logging

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from bot.keyboards.inline import reply_keyboard
from bot.models.user import Request
from core.config import ADMIN_IDS, GENERAL_ADMIN_IDS, OUTAGE_ADMIN_IDS
from core.database import SessionLocal

logger = logging.getLogger(__name__)


async def safe_send(bot: Bot, chat_id: int, text: str, **kwargs) -> bool:
    """Send a message with graceful error handling."""
    try:
        await bot.send_message(chat_id=chat_id, text=text, **kwargs)
        return True
    except TelegramForbiddenError:
        logger.warning("Cannot send to %s: bot blocked", chat_id)
    except TelegramBadRequest as e:
        logger.warning("Cannot send to %s: %s", chat_id, e)
    except Exception as e:
        logger.error("Unexpected error sending to %s: %s", chat_id, e)
    return False


def get_target_admins(category_id: str) -> list[int]:
    """Kategoriyaga qarab to'g'ri adminlar ro'yxatini qaytaradi."""
    if category_id == "outage":
        return OUTAGE_ADMIN_IDS or ADMIN_IDS
    return GENERAL_ADMIN_IDS or ADMIN_IDS


async def notify_admins(
    bot: Bot, text: str, request_id: int, user_lang: str, category_id: str = ""
) -> None:
    kb = reply_keyboard(request_id, user_lang)
    target_admins = get_target_admins(category_id)
    for admin_id in target_admins:
        try:
            msg = await bot.send_message(
                chat_id=admin_id,
                text=text,
                reply_markup=kb,
                parse_mode=ParseMode.HTML,
            )
            async with SessionLocal() as session:
                req = await session.get(Request, request_id)
                if req:
                    req.admin_message_id = msg.message_id
                    req.admin_chat_id = admin_id
                    await session.commit()
        except TelegramForbiddenError:
            logger.warning("Admin %s blocked the bot", admin_id)
        except (TelegramBadRequest, Exception) as e:
            logger.error("Could not notify admin %s: %s", admin_id, e)
