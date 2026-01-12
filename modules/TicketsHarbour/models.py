from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import String, Integer, DateTime, Boolean, func
from typing import Optional
from app.database import Base
from sqlalchemy.dialects.postgresql import JSONB


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    support_ticket_id: Mapped[str] = mapped_column(String(50), index=True)
    content: Mapped[JSONB] = mapped_column(JSONB, nullable=False)
    raised_by: Mapped[JSONB] = mapped_column(JSONB, nullable=False)
    customer_details: Mapped[Optional[JSONB]] = mapped_column(JSONB, nullable=True)
    additional_details: Mapped[Optional[JSONB]] = mapped_column(JSONB, nullable=True)
    outlet_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    api_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    assigned_agent: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    agent_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    customer_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)
    closed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True, index=True)
    is_in_trash: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    outlet: Mapped["SupportSettings"] = relationship(
        "SupportSettings", back_populates="tickets", primaryjoin="foreign(Ticket.outlet_id)==SupportSettings.outlet_id", viewonly=True)
    

class SupportSettings(Base):
    __tablename__ = "support_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    outlet_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    web_url: Mapped[str] = mapped_column(String, nullable=True)
    settings: Mapped[JSONB] = mapped_column(JSONB, nullable=True)

    tickets = relationship(
        "Ticket", back_populates="outlet", primaryjoin="foreign(Ticket.outlet_id)==SupportSettings.outlet_id", viewonly=True
    )

class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    level: Mapped[str] = mapped_column(String, nullable=False)
    department: Mapped[str] = mapped_column(String, nullable=False)
    outlet_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)