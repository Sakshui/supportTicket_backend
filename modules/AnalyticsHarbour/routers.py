from fastapi import APIRouter, Depends, Request
from app.utility import ApiResponse
from app.project_schemas import APIResponse
from app.auth import verify_jwt_token

from .controller import analytics_controller

router = APIRouter()


@router.api_route(
    "/", 
    methods=["GET"], 
    response_model=APIResponse[dict], 
    response_class=ApiResponse,
    dependencies=[Depends(verify_jwt_token)],
    openapi_extra={
        "security": [{"BearerAuth": []}]
    }
)
async def get_analytics(request: Request, auth_data=Depends(verify_jwt_token)):
    """
    Get complete analytics for the authenticated outlet.
    Returns ticket counts, closing times, top users, and top categories.
    
    **Authentication Required**: Bearer token with outlet_id in payload.
    """
    outlet_id = auth_data.get("outlet_id")
    return await analytics_controller(request, outlet_id=outlet_id)

