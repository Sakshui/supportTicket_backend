from fastapi import APIRouter, Depends, Request
from app.utility import ApiResponse
from app.project_schemas import APIResponse
from app.auth import verify_jwt_token

from .controller import *

router = APIRouter()


# ========================== AUTHENTICATED TICKET ROUTES ==========================

@router.api_route("/handler/", methods=["POST"], response_model=APIResponse[dict], response_class=ApiResponse)
async def create_tickets_authenticated(request: Request ,auth_data=Depends(verify_jwt_token)):
    outlet_id = auth_data.get("outlet_id")
    return await auth_tickets_controller(request, outlet_id=outlet_id)


@router.api_route("/handler/", methods=["GET"], response_model=APIResponse[dict], response_class=ApiResponse)
async def get_tickets_authenticated(request: Request, auth_data=Depends(verify_jwt_token)):
    outlet_id = auth_data.get("outlet_id")
    return await auth_tickets_controller(request, outlet_id=outlet_id)

@router.api_route("/handler/",methods=["PUT"],response_model=APIResponse[dict],response_class=ApiResponse)
async def update_ticket_authentication(request:Request,auth_data=Depends(verify_jwt_token)):
    outlet_id = auth_data.get("outlet_id")
    return await auth_tickets_controller(request, outlet_id=outlet_id)


@router.api_route("/handler/", methods=["DELETE"], response_model=APIResponse[dict], response_class=ApiResponse)
async def delete_tickets_authenticated(request: Request, auth_data=Depends(verify_jwt_token)):
    outlet_id = auth_data.get("outlet_id")
    return await auth_tickets_controller(request, outlet_id=outlet_id)


# ========================== UNAUTHENTICATED TICKET ROUTES ==========================

@router.api_route("/handler/shop", methods=["POST"], response_model=APIResponse[dict], response_class=ApiResponse)
async def create_tickets(request: Request):
    return await tickets_controller(request=request)


@router.api_route("/handler/shop", methods=["GET"], response_model=APIResponse[dict], response_class=ApiResponse)
async def get_tickets(request: Request):
    return await tickets_controller(request=request)


@router.api_route("/handler/shop", methods=["DELETE"], response_model=APIResponse[dict], response_class=ApiResponse)
async def delete_ticket(request: Request):
    return await tickets_controller(request=request)



# ========================== SUPPORT SETTINGS ROUTES ==========================

@router.api_route("/settings/", methods=["POST"], response_model=APIResponse[dict], response_class=ApiResponse)
async def create_support_settings(request: Request, auth_data=Depends(verify_jwt_token)):
    outlet_id = auth_data.get("outlet_id")
    
    return await support_settings_controller(request, outlet_id=outlet_id)


@router.api_route("/settings/", methods=["GET"], response_model=APIResponse[dict], response_class=ApiResponse)
async def get_support_settings(request: Request, auth_data=Depends(verify_jwt_token)):
    outlet_id = auth_data.get("outlet_id")
    return await support_settings_controller(request, outlet_id=outlet_id)


@router.api_route("/settings/", methods=["PUT"], response_model=APIResponse[dict], response_class=ApiResponse)
async def update_support_settings(request: Request, auth_data=Depends(verify_jwt_token)):
    outlet_id = auth_data.get("outlet_id")
    return await support_settings_controller(request, outlet_id=outlet_id)


@router.api_route("/settings/", methods=["DELETE"], response_model=APIResponse[dict], response_class=ApiResponse)
async def delete_support_settings(request: Request, auth_data=Depends(verify_jwt_token)):
    outlet_id = auth_data.get("outlet_id")
    return await support_settings_controller(request, outlet_id=outlet_id)


# ========================== AGENT ROUTES ==========================
@router.api_route("/agents/", methods=["POST", "GET", "PUT", "DELETE"], response_model=APIResponse[dict], response_class=ApiResponse)
async def create_agent(request: Request ,auth_data=Depends(verify_jwt_token)):
    outlet_id = auth_data.get("outlet_id")
    return await agents_controller(request, outlet_id=outlet_id)

# ========================== RATING ROUTES ==========================
# Authenticated (agent)
@router.api_route("/ratings/", methods=["POST", "GET", "PUT", "DELETE"], response_model=APIResponse[dict], response_class=ApiResponse)
async def create_agent_rating(request: Request ,auth_data=Depends(verify_jwt_token)):
    outlet_id = auth_data.get("outlet_id")
    return await agent_rating_controller(request, outlet_id=outlet_id)

# Unauthenticated (customer)
@router.api_route("/ratings/shop", methods=["POST", "GET", "PUT", "DELETE"], response_model=APIResponse[dict], response_class=ApiResponse)
async def create_customer_rating(request: Request):
    return await customer_rating_controller(request)