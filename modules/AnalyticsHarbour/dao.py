from sqlalchemy import text, select, func
from sqlalchemy.dialects.postgresql import JSONB
from typing import List, Tuple, Optional
from app.database import fetch_one, fetch_all, SupportTicketAsyncSession
from modules.TicketsHarbour.models import Ticket


class AnalyticsDao:
    
    @staticmethod
    async def get_ticket_counts(outlet_id: int) -> Tuple[int, int]:
        """
        Get total tickets and in-progress tickets count for an outlet.
        In-progress = status='assign' OR status='open'
        Returns: (total_count, in_progress_count)
        """
        query = text("""
            SELECT 
                COUNT(*) FILTER (WHERE is_in_trash = false) as total,
                COUNT(*) FILTER (
                    WHERE is_in_trash = false 
                    AND (status = 'assign' OR status = 'open')
                ) as in_progress
            FROM tickets
            WHERE outlet_id = :outlet_id
        """)
        
        async with SupportTicketAsyncSession() as session:
            result = await session.execute(query, {"outlet_id": outlet_id})
            row = result.fetchone()
            if row:
                return (row[0] or 0, row[1] or 0)
            return (0, 0)
    
    @staticmethod
    async def get_top_categories(outlet_id: int, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get top categories (departments) by ticket count for an outlet.
        Returns: List of (department, count) tuples, sorted by count descending
        """
        query = text("""
            SELECT 
                additional_details->>'department' as department,
                COUNT(*) as count
            FROM tickets
            WHERE outlet_id = :outlet_id
                AND is_in_trash = false
                AND additional_details->>'department' IS NOT NULL
            GROUP BY additional_details->>'department'
            ORDER BY count DESC
            LIMIT :limit
        """)
        
        async with SupportTicketAsyncSession() as session:
            result = await session.execute(query, {"outlet_id": outlet_id, "limit": limit})
            rows = result.fetchall()
            return [(row[0], row[1]) for row in rows if row[0]]
    
    @staticmethod
    async def get_average_closing_time(outlet_id: int) -> Optional[float]:
        """
        Get average closing time in hours for closed tickets.
        Returns: Average hours from created_at to closed_at, or None if no closed tickets
        """
        query = text("""
            SELECT 
                AVG(EXTRACT(EPOCH FROM (closed_at - created_at)) / 3600.0) as avg_hours
            FROM tickets
            WHERE outlet_id = :outlet_id
                AND is_in_trash = false
                AND status = 'close'
                AND closed_at IS NOT NULL
        """)
        
        async with SupportTicketAsyncSession() as session:
            result = await session.execute(query, {"outlet_id": outlet_id})
            row = result.fetchone()
            if row and row[0] is not None:
                return float(row[0])
            return None
    
    @staticmethod
    async def get_closing_time_comparison(outlet_id: int) -> Tuple[Optional[float], Optional[float]]:
        """
        Get average closing time for today and yesterday.
        Returns: (today_avg_hours, yesterday_avg_hours)
        """
        query = text("""
            SELECT 
                AVG(EXTRACT(EPOCH FROM (closed_at - created_at)) / 3600.0) FILTER (
                    WHERE DATE(closed_at) = CURRENT_DATE
                ) as today_avg,
                AVG(EXTRACT(EPOCH FROM (closed_at - created_at)) / 3600.0) FILTER (
                    WHERE DATE(closed_at) = CURRENT_DATE - INTERVAL '1 day'
                ) as yesterday_avg
            FROM tickets
            WHERE outlet_id = :outlet_id
                AND is_in_trash = false
                AND status = 'close'
                AND closed_at IS NOT NULL
                AND DATE(closed_at) >= CURRENT_DATE - INTERVAL '1 day'
        """)
        
        async with SupportTicketAsyncSession() as session:
            result = await session.execute(query, {"outlet_id": outlet_id})
            row = result.fetchone()
            if row:
                today_avg = float(row[0]) if row[0] is not None else None
                yesterday_avg = float(row[1]) if row[1] is not None else None
                return (today_avg, yesterday_avg)
            return (None, None)
    
    @staticmethod
    async def get_top_closing_users(outlet_id: int, limit: int = 5) -> List[Tuple[int, int]]:
        """
        Get top users who closed most tickets (by assigned_agent).
        Returns: List of (user_id, closed_count) tuples, sorted by count descending
        """
        query = text("""
            SELECT 
                assigned_agent as user_id,
                COUNT(*) as closed_count
            FROM tickets
            WHERE outlet_id = :outlet_id
                AND is_in_trash = false
                AND status = 'close'
                AND assigned_agent IS NOT NULL
            GROUP BY assigned_agent
            ORDER BY closed_count DESC
            LIMIT :limit
        """)
        
        async with SupportTicketAsyncSession() as session:
            result = await session.execute(query, {"outlet_id": outlet_id, "limit": limit})
            rows = result.fetchall()
            return [(row[0], row[1]) for row in rows if row[0]]

