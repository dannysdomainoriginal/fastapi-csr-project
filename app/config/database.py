from collections.abc import AsyncGenerator
from datetime import datetime
from uuid import uuid4

from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, event, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship

from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.pool.base import _ConnectionRecord

from app.config.security import hash_password, verify_password

DATABASE_URL = "sqlite+aiosqlite:///./app_database.db"


# ---------------------------------------------------------------------------- #
#                                     MODEL                                    #
# ---------------------------------------------------------------------------- #
class Base(DeclarativeBase):
    pass


class Post(Base):
    __tablename__ = "posts"

    # Using Mapped[] provides perfect type-checking
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, default=False)

    author: Mapped["User"] = relationship(lazy="joined")
    author_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # posts: Mapped[list["Post"]] = relationship(
    #     back_populates="author",
    #     cascade="all, delete-orphan",
    #     # lazy="selectin", not safe for scale, prefer barricading with 'raise'
    # )

    @property
    def password(self) -> None:
        raise AttributeError("Password is write-only")

    @password.setter
    def password(self, plain_password: str) -> None:
        self.password_hash = hash_password(plain_password)

    def verify_password(self, plain_password: str) -> bool:
        return verify_password(plain_password, self.password_hash)


engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)


# ---------------------------------------------------------------------------- #
#                          SQLITE CASCADE ENFORCEMENT                          #
# ---------------------------------------------------------------------------- #
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection: DBAPIConnection, _crecord: _ConnectionRecord):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# ---------------------------------------------------------------------------- #
#                               UTILITY FUNCTIONS                              #
# ---------------------------------------------------------------------------- #
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
