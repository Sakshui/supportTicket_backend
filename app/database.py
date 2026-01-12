from collections.abc import Callable
from typing import AsyncGenerator, Optional, TypeVar, Any, Type, Mapping
from sqlalchemy import delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import Select, Executable

from app.settings import get_settings
settings = get_settings()

Base = declarative_base()
T = TypeVar("T")

# ------------------------------------------ Database Engines & Sessions ------------------------------------------

support_tickets_engine = create_async_engine(
    settings.db.support_tickets_url,
    echo=False,
    pool_pre_ping=True
)

SupportTicketAsyncSession: Callable[[], AsyncSession] = sessionmaker(
    bind=support_tickets_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

SessionLocal = SupportTicketAsyncSession


# ------------------------------------------ Async Session Dependencies ------------------------------------------

async def get_support_ticket_db() -> AsyncGenerator[AsyncSession, None]:
    async with SupportTicketAsyncSession() as session:
        yield session


# ------------------------------------------ Session Factory ------------------------------------------

def get_session_factory(db_name: Optional[str] = None) -> Callable[[], AsyncSession]:
    return SupportTicketAsyncSession


# ------------------------------------------ Generic CRUD Utilities ------------------------------------------

async def create(instance: T, db_name: Optional[str] = None) -> int:
    session_factory = get_session_factory(db_name)
    async with session_factory() as session:
        try:
            async with session.begin():
                session.add(instance)
                await session.flush()
                return instance.id
        except Exception:
            await session.rollback()
            raise


async def update(instance: T, db_name: Optional[str] = None) -> int:
    session_factory = get_session_factory(db_name)
    async with session_factory() as session:
        try:
            async with session.begin():
                await session.merge(instance)
                await session.flush()
                return instance.id
        except Exception:
            await session.rollback()
            raise


async def update_fields(model: Type[T], id: int, data: dict, db_name: Optional[str] = None) -> int:
    session_factory = get_session_factory(db_name)
    async with session_factory() as session:
        try:
            async with session.begin():
                instance = await session.get(model, id)
                if not instance:
                    raise ValueError(f"{model.__name__} with id {id} not found")

                for key, value in data.items():
                    setattr(instance, key, value)

                await session.flush()
                return instance.id
        except Exception:
            await session.rollback()
            raise


async def delete(instance: T, db_name: Optional[str] = None) -> None:
    session_factory = get_session_factory(db_name)
    async with session_factory() as session:
        try:
            async with session.begin():
                await session.delete(instance)
        except Exception:
            await session.rollback()
            raise


async def delete_by_id(model: Type[T], id: int, db_name: Optional[str] = None) -> None:
    session_factory = get_session_factory(db_name)
    async with session_factory() as session:
        try:
            async with session.begin():
                stmt = sa_delete(model).where(model.id == id)
                await session.execute(stmt)
        except Exception:
            await session.rollback()
            raise


async def fetch_one(query: Select, db_name: Optional[str] = None) -> Optional[Any]:
    session_factory = get_session_factory(db_name)
    async with session_factory() as session:
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def fetch_all(query: Select, db_name: Optional[str] = None) -> list[Any]:
    session_factory = get_session_factory(db_name)
    async with session_factory() as session:
        result = await session.execute(query)
        return result.scalars().all()


async def execute_query(query: Executable, db_name: Optional[str] = None) -> Any:
    session_factory = get_session_factory(db_name)
    async with session_factory() as session:
        try:
            async with session.begin():
                result = await session.execute(query)
                return result
        except Exception:
            await session.rollback()
            raise
