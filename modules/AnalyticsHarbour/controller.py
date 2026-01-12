from fastapi import Request
from typing import Optional
from app.utility import ApiResponse
from app.project_schemas import APIResponse
from .services import AnalyticsService


async def analytics_controller(request: Request, outlet_id: Optional[int] = None) -> ApiResponse:
    """
    Controller for analytics endpoint.
    Extracts outlet_id from JWT and fetches analytics data.
    """
    if not outlet_id:
        return APIResponse.error(
            message="outlet_id is required",
            code=400
        )
    
    try:
        analytics_data = await AnalyticsService.get_basic_analytics(outlet_id=outlet_id)
        return APIResponse.success(
            data=analytics_data.model_dump(),
            message="Analytics fetched successfully",
            code=200
        )
    except Exception as e:
        return APIResponse.error(
            message=f"Error fetching analytics: {str(e)}",
            code=500
        )

