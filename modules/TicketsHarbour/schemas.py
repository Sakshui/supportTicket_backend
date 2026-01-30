from typing import Optional, Dict, Any, List,Union
from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from enum import Enum

# ================================================ Tickets ====================================================================

class PriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatusEnum(str, Enum):
    OPEN = "open"
    PENDING = "pending"
    ASSIGNED = "assigned"
    CLOSED = "closed"

    @classmethod
    def _missing_(cls, value):
        """
        Allow case-insensitive matching:
            'OPEN', 'open', 'Open', 'OpEn' → TicketStatusEnum.OPEN
        """
        if isinstance(value, str):
            lower = value.lower()
            for member in cls:
                if member.value == lower:
                    return member
        return None

class TicketContent(BaseModel):
    subject: str
    description: Optional[str] = None
    attachment: Optional[List[str]] = None

class RaisedBy(BaseModel):
    user_id: str
    user_type: str
    email: Optional[str] = None
    name: Optional[str]  = None

class CustomerDetails(BaseModel):
    customer_id: int
    customer_name: str
    customer_email: str

class AdditionalDetails(BaseModel):
    tags: Optional[List[str]] = None
    priority: PriorityEnum = PriorityEnum.LOW
    department: str

class SourceInfo(BaseModel):
    browser: Optional[str] = None
    os: Optional[str] = None
    device: Optional[str] = None
    raw_user_agent: Optional[str] = None

class TicketBase(BaseModel):
    support_ticket_id: str
    content: Optional[TicketContent]
    raised_by: Optional[RaisedBy]
    customer_details: Optional[CustomerDetails] = None
    additional_details: AdditionalDetails
    outlet_id: int
    api_key: Optional[str] = None
    source: Optional[SourceInfo] = None 
    status: TicketStatusEnum = TicketStatusEnum.PENDING
    assigned_agent: Optional[int] = None

    model_config = {"from_attributes": True}


class TicketUpdateIn(BaseModel):
    id: int
    outlet_id: int
    status: Optional[TicketStatusEnum]
    assigned_agent: Optional[int]

class TicketRead(TicketBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_in_trash: bool

class TicketRatingIn(BaseModel):
    id: int
    rating: int = Field(..., ge=1, le=10)
    
    model_config = {"from_attributes": True}


# ================================================ SupportSettings ====================================================================

class SettingJSON(BaseModel):
    prefix: Optional[str]       = Field(default="TKT")
    start_no: Optional[str]     = Field(default="001")
    auto_assign: Optional[bool] = Field(default=True)
    email_required: bool        = Field(default=True)


class SupportSettingsBase(BaseModel):
    outlet_id: int
    web_url: str
    settings: SettingJSON

    model_config = {"from_attributes": True}


class SupportSettingsRead(SupportSettingsBase):
    id: int



class SupportSettingsUpdateIn(SupportSettingsBase):
    id: int


# ================================================ Agents ====================================================================

class AgentLevelEnum(str, Enum):
    EXECUTIVE = "executive"
    MANAGER = "manager"
    ADMIN = "admin"
    MERCHANT = "merchant"

class AgentStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended" # May be used in the future

class AgentCategoryEnum(str, Enum):
    GENERAL = "general"
    BILLING = "billing"
    TECHNICAL = "technical"
    PRODUCT = "product"
    SHIPPING = "shipping"
    ESCALATION = "escalation"

class AgentSubCategoryEnum(str, Enum):
    INVOICE = "invoice"
    REFUND = "refund"
    PAYMENT = "payment"
    LOGIN = "login"
    BUG = "bug"
    FEATURE = "feature"
    DELIVERY = "delivery"
    DELAY = "delay"
    URGENT = "urgent"


CATEGORY_SUBCATEGORY_MAP = {
    AgentCategoryEnum.GENERAL: {AgentSubCategoryEnum.URGENT},
    AgentCategoryEnum.BILLING: {
        AgentSubCategoryEnum.INVOICE,
        AgentSubCategoryEnum.REFUND,
        AgentSubCategoryEnum.PAYMENT,
    },
    AgentCategoryEnum.TECHNICAL: {
        AgentSubCategoryEnum.LOGIN,
        AgentSubCategoryEnum.BUG,
    },
    AgentCategoryEnum.PRODUCT: {
        AgentSubCategoryEnum.FEATURE,
        AgentSubCategoryEnum.BUG,
    },
    AgentCategoryEnum.SHIPPING: {
        AgentSubCategoryEnum.DELIVERY,
        AgentSubCategoryEnum.DELAY,
    },
    AgentCategoryEnum.ESCALATION: {AgentSubCategoryEnum.URGENT},
}

class AgentWorkingHours(BaseModel):
    start: str  # "09:00"
    end: str    # "17:00"

class AgentBase(BaseModel):
    user_id: int
    level: AgentLevelEnum = AgentLevelEnum.ADMIN
    department: str
    outlet_id: int
    skills: Optional[List[str]] = None
    status: AgentStatusEnum
    category: AgentCategoryEnum
    sub_category: AgentSubCategoryEnum
    hired_at: datetime
    working_hours: AgentWorkingHours
    working_days: List[str]
    timezone: str
    languages: List[str]
    bio: Optional[str] = None

    @model_validator(mode="after")
    def validate_category_pair(self):
        allowed = CATEGORY_SUBCATEGORY_MAP[self.category]
        if self.sub_category not in allowed:
            raise ValueError(
                f"Invalid sub_category '{self.sub_category}' "
                f"for category '{self.category}'"
            )
        return self


    model_config = {"from_attributes": True, "use_enum_values": True}


class AgentRead(AgentBase):
    id: int
    created_at: datetime
    updated_at: datetime

class AgentUpdateIn(BaseModel):
    id: int
    level: Optional[AgentLevelEnum] = None
    department: Optional[str] = None
    outlet_id: Optional[int] = None
    skills: Optional[List[str]] = None
    status: Optional[AgentStatusEnum] = None
    category: Optional[AgentCategoryEnum] = None
    sub_category: Optional[AgentSubCategoryEnum] = None
    hired_at: Optional[datetime] = None
    working_hours: Optional[AgentWorkingHours] = None
    working_days: Optional[List[str]] = None
    timezone: Optional[str] = None
    languages: Optional[List[str]] = None
    bio: Optional[str] = None
    
    @model_validator(mode="after")
    def validate_category_pair(self):
        if self.category is not None and self.sub_category is not None:    
            allowed = CATEGORY_SUBCATEGORY_MAP[self.category]
            if self.sub_category not in allowed:
                raise ValueError(
                    f"Invalid sub_category '{self.sub_category}' "
                    f"for category '{self.category}'"
                )
            return self