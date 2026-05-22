from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.user import User


async def get_user(session: AsyncSession, telegram_id: int) -> Optional[User]:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def get_or_create_user(
    session: AsyncSession, telegram_id: int, username: str | None
) -> User:
    user = await get_user(session, telegram_id)
    if not user:
        user = User(telegram_id=telegram_id, username=username or "")
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def get_user_lang(session: AsyncSession, telegram_id: int) -> str:
    user = await get_user(session, telegram_id)
    return user.lang_code if user and user.lang_code else "uz"
