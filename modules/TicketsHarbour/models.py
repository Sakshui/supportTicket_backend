from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import String, Integer, DateTime, Boolean, func, text, Enum as SAEnum, Text
from typing import Optional
from app.database import Base
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from datetime import datetime

class Ticket(Base):
    __tablename__ = "tickets"

    # Identity & tenancy
    id: Mapped[int] = mapped_column(primary_key=True)
    support_ticket_id: Mapped[str] = mapped_column(String(50), index=True)
    outlet_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    api_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Core ticket data (JSONB)
    content: Mapped[JSONB] = mapped_column(JSONB, nullable=False)
    raised_by: Mapped[JSONB] = mapped_column(JSONB, nullable=False)
    customer_details: Mapped[Optional[JSONB]] = mapped_column(JSONB, nullable=True)
    additional_details: Mapped[Optional[JSONB]] = mapped_column(JSONB, nullable=True)
    source: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Assignment & status
    status: Mapped[str] = mapped_column(String(20), default="pending", server_default=text("'pending'"), nullable=False)
    assigned_agent: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_in_trash: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"), nullable=False)

    # Ratings
    agent_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    customer_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    outlet: Mapped["SupportSettings"] = relationship(
        "SupportSettings", back_populates="tickets",
        primaryjoin="foreign(Ticket.outlet_id)==SupportSettings.outlet_id",
        viewonly=True,
    )

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

    # Identity & tenancy
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    outlet_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Core agent info
    level: Mapped[str] = mapped_column(String, nullable=False)
    department: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    hired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Expertise
    skills: Mapped[list[str]] = mapped_column(JSONB, default=list, server_default=text("'[]'::jsonb"), nullable=False)
    languages: Mapped[list[str]] = mapped_column(JSONB, default=list, server_default=text("'[]'::jsonb"), nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Availability
    working_hours: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    working_days: Mapped[list[str]] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    timezone: Mapped[str] = mapped_column(String(50), nullable=False)

    # Classification
    category: Mapped[str] = mapped_column(String, nullable=False)
    sub_category: Mapped[str] = mapped_column(String, nullable=False)

    # System timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
