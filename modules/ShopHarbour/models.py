from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import String, Integer, DateTime, Boolean, func
from typing import Optional, List
from app.database import Base
from enum import Enum
from sqlalchemy.dialects.postgresql import JSONB




class Shop(Base):
    __tablename__ = "shopify_shop"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    outlet_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    shop: Mapped[str] = mapped_column(String, nullable=False)
    api_key: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    access_token: Mapped[str] = mapped_column(String(250), nullable= True)
