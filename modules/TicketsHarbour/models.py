from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import String, Integer, DateTime, Boolean, func, text, Enum as SAEnum, Text, ForeignKey, UniqueConstraint, Index
from typing import Optional, Any
from app.database import Base
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from datetime import datetime

class Ticket(Base):
    __tablename__ = "tickets"

    # Identity & tenancy
    id: Mapped[int]                = mapped_column(primary_key=True)
    support_ticket_id: Mapped[str] = mapped_column(String(50), index=True)
    outlet_id: Mapped[int]         = mapped_column(Integer, nullable=False, index=True)
    api_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Content data
    subject: Mapped[str]               = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    attachment: Mapped[Optional[str]]  = mapped_column(String, nullable=True)

    # Ticket issuer & customer data
    raised_by: Mapped[str]                    = mapped_column(String, nullable=False) # customer or agent
    raised_by_id: Mapped[int]                 = mapped_column(Integer, nullable=False) # customer_id or agent_id based on raised_by
    customer_details: Mapped[Optional[JSONB]] = mapped_column(JSONB, nullable=True)

    # Additional details
    tags: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    priority: Mapped[str]        = mapped_column(String, nullable=False)
    department: Mapped[str]      = mapped_column(String, nullable=False)

    # Ticket outlet issue type, category, sub-category & snapshots
    outlet_issue_id: Mapped[int] = mapped_column(ForeignKey("outlet_issues.id"), nullable=False, index=True)
    outlet_category_id: Mapped[int] = mapped_column(ForeignKey("outlet_categories.id"), nullable=False, index=True)
    outlet_sub_category_id: Mapped[int] = mapped_column(ForeignKey("outlet_sub_categories.id"), nullable=False, index=True)

    issue_name_snapshot: Mapped[str] = mapped_column(String, nullable=False)
    category_name_snapshot: Mapped[str] = mapped_column(String, nullable=False)
    sub_category_name_snapshot: Mapped[str] = mapped_column(String, nullable=False)

    # Device user-data
    source: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Assignment & status
    status: Mapped[str]                                             = mapped_column(String(20), default="pending", server_default=text("'pending'"), nullable=False)
    assigned_agent_id: Mapped[int]                                  = mapped_column(Integer, ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    previous_assigned_agent_id: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb")) # id, re-assigned timestamps
    is_trash: Mapped[bool]                                          = mapped_column(Boolean, default=False, server_default=text("false"), nullable=False)

    # Ratings
    agent_rating: Mapped[Optional[int]]    = mapped_column(Integer, nullable=True)
    customer_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Timestamps
    created_at: Mapped[datetime]          = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at: Mapped[datetime]          = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    assigned_agent: Mapped["Agent"] = relationship( "Agent", back_populates="tickets", foreign_keys=[assigned_agent_id])
    outlet: Mapped["SupportSettings"] = relationship("SupportSettings", back_populates="tickets", primaryjoin="foreign(Ticket.outlet_id)==SupportSettings.outlet_id", viewonly=True,)
    outlet_issue: Mapped["OutletIssue"] = relationship("OutletIssue", foreign_keys=[outlet_issue_id],)
    outlet_category: Mapped["OutletCategory"] = relationship("OutletCategory", foreign_keys=[outlet_category_id],)
    outlet_sub_category: Mapped["OutletSubCategory"] = relationship("OutletSubCategory", foreign_keys=[outlet_sub_category_id],)


class SupportSettings(Base):
    __tablename__ = "support_settings"

    id: Mapped[int]         = mapped_column(Integer, primary_key=True, index=True)
    outlet_id: Mapped[int]  = mapped_column(Integer, unique=True, index=True)
    web_url: Mapped[str]    = mapped_column(String, nullable=True)
    settings: Mapped[JSONB] = mapped_column(JSONB, nullable=True)

    tickets = relationship("Ticket", back_populates="outlet", primaryjoin="foreign(Ticket.outlet_id)==SupportSettings.outlet_id", viewonly=True)


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

class SubCategory(Base):
    __tablename__ = "sub_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

class IssueCategoryMap(Base):
    __tablename__ = "issue_category_map"

    issue_id: Mapped[int]    = mapped_column(ForeignKey("issues.id", ondelete="CASCADE"), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("issue_id", "category_id", name="uq_issue_category"),
        Index("ix_issue_category_issue_id", "issue_id"),
        Index("ix_issue_category_category_id", "category_id"),
    )

class CategorySubCategoryMap(Base):
    __tablename__ = "category_subcategory_map"

    category_id: Mapped[int]     = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
    sub_category_id: Mapped[int] = mapped_column(ForeignKey("sub_categories.id", ondelete="CASCADE"), primary_key=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("category_id", "sub_category_id", name="uq_category_subcategory"),
        Index("ix_category_subcategory_category_id", "category_id"),
        Index("ix_category_subcategory_sub_category_id", "sub_category_id"),
    )

class OutletIssue(Base):
    __tablename__ = "outlet_issues"

    id: Mapped[int]        = mapped_column(Integer, primary_key=True)
    outlet_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    issue_id: Mapped[Optional[int]] = mapped_column(ForeignKey("issues.id"), nullable=True, index=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=False)

    is_custom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_trash: Mapped[bool]  = mapped_column(Boolean, default=False, server_default=text("false"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("outlet_id", "slug", name="uq_outlet_issue_slug"),
    )

class OutletCategory(Base):
    __tablename__ = "outlet_categories"

    id: Mapped[int]        = mapped_column(Integer, primary_key=True)
    outlet_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True, index=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=False)

    is_custom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_trash: Mapped[bool]  = mapped_column(Boolean, default=False, server_default=text("false"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("outlet_id", "slug", name="uq_outlet_category_slug"),
    )

class OutletSubCategory(Base):
    __tablename__ = "outlet_sub_categories"

    id: Mapped[int]        = mapped_column(Integer, primary_key=True)
    outlet_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    sub_category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sub_categories.id"), nullable=True, index=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=False)

    is_custom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_trash: Mapped[bool]  = mapped_column(Boolean, default=False, server_default=text("false"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("outlet_id", "slug", name="uq_outlet_subcategory_slug"),
    )

class OutletIssueCategoryMap(Base):
    __tablename__ = "outlet_issue_category_map"

    outlet_issue_id: Mapped[int]    = mapped_column(ForeignKey("outlet_issues.id", ondelete="CASCADE"), primary_key=True)
    outlet_category_id: Mapped[int] = mapped_column(ForeignKey("outlet_categories.id", ondelete="CASCADE"), primary_key=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint(
            "outlet_issue_id",
            "outlet_category_id",
            name="uq_outlet_issue_category"
        ),
    )

class OutletCategorySubCategoryMap(Base):
    __tablename__ = "outlet_category_subcategory_map"

    outlet_category_id: Mapped[int]     = mapped_column(ForeignKey("outlet_categories.id", ondelete="CASCADE"), primary_key=True)
    outlet_sub_category_id: Mapped[int] = mapped_column(ForeignKey("outlet_sub_categories.id", ondelete="CASCADE"), primary_key=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint(
            "outlet_category_id",
            "outlet_sub_category_id",
            name="uq_outlet_category_subcategory"
        ),
    )

 
class Agent(Base):
    __tablename__ = "agents"

    # Identity & tenancy
    id: Mapped[int]        = mapped_column(Integer, primary_key=True)
    outlet_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    user_id: Mapped[int]   = mapped_column(Integer, nullable=False, index=True)
    agent_first_name: Mapped[str] = mapped_column(String, nullable=False)
    agent_last_name: Mapped[str] = mapped_column(String, nullable=False)
    agent_email: Mapped[str] = mapped_column(String, nullable=False)
    country_code: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)

    # Core agent info
    level: Mapped[str]          = mapped_column(String, nullable=False)
    department: Mapped[str]     = mapped_column(String, nullable=False)
    status: Mapped[str]         = mapped_column(String, nullable=False)
    hired_at: Mapped[datetime]  = mapped_column(DateTime(timezone=True), nullable=False)

    # Expertise
    skills: Mapped[list[str]]    = mapped_column(JSONB, default=list, server_default=text("'[]'::jsonb"), nullable=False)
    languages: Mapped[list[str]] = mapped_column(JSONB, default=list, server_default=text("'[]'::jsonb"), nullable=False)
    bio: Mapped[Optional[str]]   = mapped_column(Text, nullable=True)
    timezone: Mapped[str]        = mapped_column(String(50), nullable=False)

    # Availability
    working_hours: Mapped[dict]     = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    working_days: Mapped[list[str]] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))

    # Classification
    category: Mapped[str]       = mapped_column(String, nullable=False)
    sub_category: Mapped[str]   = mapped_column(String, nullable=False)

    # System timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relations
    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="assigned_agent")