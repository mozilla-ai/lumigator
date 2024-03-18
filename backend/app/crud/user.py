from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def count_users(db: AsyncSession):
    stmt = select(func.count()).select_from(User)
    return await db.scalar(stmt)


async def create_user(db: AsyncSession, *, name: str):
    entry = User(name=name)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def get_user_by_id(db: AsyncSession, *, id: UUID):
    stmt = select(User).where(User.id == id)
    return await db.scalar(stmt)


async def get_user_by_name(db: AsyncSession, *, name: str):
    stmt = select(User).where(User.name == name)
    return await db.scalar(stmt)


async def get_users(db: AsyncSession, *, skip: int = 0, limit: int = 100):
    stmt = select(User).offset(skip).limit(limit)
    return (await db.scalars(stmt)).all()
