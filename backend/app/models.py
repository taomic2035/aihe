import uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, Float, DateTime, ForeignKey
from datetime import datetime


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at: Mapped[str] = mapped_column(String, default=lambda: datetime.utcnow().isoformat())
    region: Mapped[str] = mapped_column(String, nullable=True)
    tier: Mapped[str] = mapped_column(String, nullable=True)


class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    version: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[str] = mapped_column(String, default=lambda: datetime.utcnow().isoformat())


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"))
    user_id: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)  # user/assistant/system
    content: Mapped[str] = mapped_column(Text)
    modality: Mapped[str] = mapped_column(String, default="text")
    created_at: Mapped[str] = mapped_column(String, default=lambda: datetime.utcnow().isoformat())


class Memory(Base):
    __tablename__ = "memories"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    type: Mapped[str] = mapped_column(String)  # episodic/semantic
    content: Mapped[str] = mapped_column(Text)
    embedding_id: Mapped[str] = mapped_column(String, nullable=True)
    graph_node_id: Mapped[str] = mapped_column(String, nullable=True)
    importance: Mapped[float] = mapped_column(Float, default=0.5)
    created_at: Mapped[str] = mapped_column(String, default=lambda: datetime.utcnow().isoformat())
    deleted_at: Mapped[str] = mapped_column(String, nullable=True)


class MemoryAudit(Base):
    __tablename__ = "memory_audit"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    memory_id: Mapped[str] = mapped_column(String, ForeignKey("memories.id"))
    action: Mapped[str] = mapped_column(String)  # create/delete/update
    actor: Mapped[str] = mapped_column(String)
    at: Mapped[str] = mapped_column(String, default=lambda: datetime.utcnow().isoformat())
