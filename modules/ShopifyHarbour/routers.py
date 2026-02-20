from fastapi import APIRouter, Depends, Request
from app.utility import ApiResponse
from app.project_schemas import APIResponse
from app.auth import verify_jwt_token

from .controller import *

router = APIRouter()

# ========================== UNAUTHENTICATED TICKET ROUTES ==========================

@router.api_route("/handler/shop", methods=["POST"], response_model=APIResponse[dict], response_class=ApiResponse)
async def create_tickets(request: Request):
    return await tickets_controller(request=request)


@router.api_route("/handler/shop", methods=["GET"], response_model=APIResponse[dict], response_class=ApiResponse)
async def get_tickets(request: Request):
    return await tickets_controller(request=request)

#-------close ticket--------
@router.api_route("/handler/shop/close", methods=["POST"], response_model=APIResponse[dict], response_class=ApiResponse)
async def close_ticket(request: Request):
    return await close_ticket_controller(request=request)

# ========================== RATING ROUTES ==========================

# Unauthenticated (customer)
@router.api_route("/ratings/shop", methods=["POST", "GET", "PUT", "DELETE"], response_model=APIResponse[dict], response_class=ApiResponse)
async def create_customer_rating(request: Request):
    return await customer_rating_controller(request)