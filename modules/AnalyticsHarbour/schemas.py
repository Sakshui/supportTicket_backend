from typing import List, Optional
from pydantic import BaseModel


class TicketCounts(BaseModel):
    total: int
    in_progress: int


class CategoryCount(BaseModel):
    department: str
    count: int


class ClosingTime(BaseModel):
    average_hours: Optional[float] = None
    today_avg_hours: Optional[float] = None
    yesterday_avg_hours: Optional[float] = None
    change_percent: Optional[float] = None


class TopUser(BaseModel):
    user_id: int
    closed_count: int


class AnalyticsResponse(BaseModel):
    ticket_counts: TicketCounts
    closing_time: Optional[ClosingTime] = None
    top_users: List[TopUser]
    top_categories: List[CategoryCount]

