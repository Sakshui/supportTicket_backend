from typing import Optional
from .dao import AnalyticsDao
from .schemas import AnalyticsResponse, TicketCounts, CategoryCount, ClosingTime, TopUser


class AnalyticsService:
    
    @staticmethod
    async def get_basic_analytics(outlet_id: int) -> AnalyticsResponse:
        """
        Get complete analytics for an outlet.
        Returns ticket counts, closing times, top users, and top categories.
        """
        # Get ticket counts
        total_count, in_progress_count = await AnalyticsDao.get_ticket_counts(outlet_id)
        
        # Get closing time metrics
        avg_closing_time = await AnalyticsDao.get_average_closing_time(outlet_id)
        today_avg, yesterday_avg = await AnalyticsDao.get_closing_time_comparison(outlet_id)
        
        # Calculate change percent
        change_percent = None
        if today_avg is not None and yesterday_avg is not None and yesterday_avg > 0:
            change_percent = ((today_avg - yesterday_avg) / yesterday_avg) * 100
        
        # Get top users
        top_users_data = await AnalyticsDao.get_top_closing_users(outlet_id, limit=5)
        top_users = [
            TopUser(user_id=user_id, closed_count=count)
            for user_id, count in top_users_data
        ]
        
        # Get top categories
        top_categories_data = await AnalyticsDao.get_top_categories(outlet_id, limit=10)
        top_categories = [
            CategoryCount(department=dept, count=count)
            for dept, count in top_categories_data
        ]
        
        # Build response
        ticket_counts = TicketCounts(
            total=total_count,
            in_progress=in_progress_count
        )
        
        closing_time = None
        if avg_closing_time is not None or today_avg is not None or yesterday_avg is not None:
            closing_time = ClosingTime(
                average_hours=avg_closing_time,
                today_avg_hours=today_avg,
                yesterday_avg_hours=yesterday_avg,
                change_percent=change_percent
            )
        
        return AnalyticsResponse(
            ticket_counts=ticket_counts,
            closing_time=closing_time,
            top_users=top_users,
            top_categories=top_categories
        )

