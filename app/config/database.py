from collections.abc import AsyncGenerator
from datetime import datetime
import uuid

from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, event, func, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.config.security import hash_password, verify_password
from app.config.settings import settings

DATABASE_URL = settings.database_url
print(f"Using database URL: {DATABASE_URL}")


# ---------------------------------------------------------------------------- #
#                                     MODEL                                    #
# ---------------------------------------------------------------------------- #
class Base(DeclarativeBase):
    pass


class Post(Base):
    __tablename__ = "posts"

    # Using Mapped[] provides perfect type-checking
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
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


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    priority: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)

    author: Mapped["User"] = relationship(lazy="raise")
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

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
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


engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
)

async_session = async_sessionmaker(engine, expire_on_commit=False)


# ---------------------------------------------------------------------------- #
#                               UTILITY FUNCTIONS                              #
# ---------------------------------------------------------------------------- #
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
