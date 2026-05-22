__version__ = "0.2.0"

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.handlers import admin, fallback, profile, register, request, start
from core.config import BOT_TOKEN
from core.database import Base, engine

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="Ro'yxatdan o'tish"),
        BotCommand(command="profile", description="Profilimni ko'rish"),
        BotCommand(command="request", description="Ariza yuborish"),
        BotCommand(command="help", description="Yordam"),
        BotCommand(command="cancel", description="Bekor qilish"),
        BotCommand(command="requests", description="Arizalar ro'yxati (admin)"),
    ]
    await bot.set_my_commands(commands)


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(register.router)
    dp.include_router(request.router)
    dp.include_router(admin.router)
    dp.include_router(profile.router)
    dp.include_router(fallback.router)

    await set_commands(bot)
    logger.info("Bot started.")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
