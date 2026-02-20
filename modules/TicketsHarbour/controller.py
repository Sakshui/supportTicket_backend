from fastapi import Request
from typing import Optional
from app.utility import ApiResponse, get_request_data
from app.project_schemas import APIResponse
from user_agents import parse

from .services import *


# ========================== AUTHENTICATED TICKET CONTROLLER ==========================

async def auth_tickets_controller(request: Request, outlet_id: Optional[int] = None) -> ApiResponse:
    data = await get_request_data(request.headers.get("content-type", ""), request)
    data.update({"outlet_id": outlet_id})

    # Device detection
    user_agent_str = request.headers.get("user-agent", "")
    ua = parse(user_agent_str)

    if ua.is_mobile:
        device_type = "Mobile"
    elif ua.is_tablet:
        device_type = "Tablet"
    elif ua.is_pc:
        device_type = "Desktop"
    else:
        device_type = "Unknown"

    source_payload = {
        "browser": ua.browser.family,
        "os": ua.os.family,
        "device": device_type,
        "raw_user_agent": user_agent_str
    }

    if request.method in ("POST", "PUT"):
        data["source"] = source_payload
    
    method = request.method

    match method:
        case "POST":
            result, status_code = await AuthTicketService.save(**data)
            message = "Tickets send successfully"
        case "GET":
            result, status_code = await AuthTicketService.get_auth_paginated_tickets(**data)
            message = "Tickets fetched successfully"
        case "PUT":
            result, status_code = await AuthTicketService.update(**data)
            message = "Tickets updated successfully"
        case "DELETE":
            result, status_code = await AuthTicketService.delete(**data)
            message = "Tickets deleted successfully"
        case _:
            return APIResponse.error(message="Method not allowed", code=405)

    return APIResponse.success(data=result, message=message, code=status_code)


async def auth_tickets_stats_controller(request: Request, outlet_id: Optional[int] = None) -> ApiResponse:
    data = await get_request_data(request.headers.get("content-type", ""), request)
    
    method = request.method
    
    if method != "GET":
        return APIResponse.error(message="Method not allowed", code=405)
    
    result, status_code = await AuthTicketService.get_ticket_stats(**data)
    message = "Tickets stat fetched successfully"
    
    return APIResponse.success(data=result, message=message, code=status_code)

# ============================================== UNAUTHENTICATED CUSTOMER TICKET CONTROLLER ========================================

# async def tickets_controller(request: Request) -> ApiResponse:   
#     data = await get_request_data(request.headers.get("content-type", ""), request)

#     web_url = data.get("web_url")
#     customer_id = data.get("customer_details", {}).get("customer_id") or data.get("customer_id")
#     email = data.get("raised_by", {}).get("email") or data.get("email")

#     if not web_url:
#         return APIResponse.error(message="Missing param web_url", code=400)

#     if not customer_id or not email:
#         return APIResponse.error(message="customer_id or email not found", code=400)

#     method = request.method

#     match method:
#         case "POST":
#                 result, status_code = await TicketService.save(**data)
#                 message = "Tickets send successfully"
#         case "GET":
#             support_ticket_id = data.get("support_ticket_id")
#             if support_ticket_id:
#                 result, status_code = await TicketService.get_by_support_ticket_id(support_ticket_id)
#             else:
#                 result, status_code = await TicketService.filters(**data)
#                 message = "Tickets fetched successfully"
#         case "PUT":
#             result, status_code = await TicketService.update(**data)
#             message = "Tickets updated successfully"
#         case "DELETE":
#             result, status_code = await TicketService.delete(**data)
#             message = "Tickets deleted successfully"
#         case _:
#             return APIResponse.error(message="Method not allowed", code=405)

#     return APIResponse.success(data=result, message=message, code=status_code)

# ========================== SUPPORT SETTINGS CONTROLLER ==========================

async def support_settings_controller(request: Request, outlet_id: Optional[int]) -> ApiResponse:
    data = await get_request_data(request.headers.get("content-type", ""), request)
    data.update({"outlet_id": outlet_id})

    method = request.method

    match method:
        case "POST":
            result, status_code = await SupportSettingsService.save(**data)
            message = "SupportSettings created successfully"

        case "GET":
            result, status_code = await SupportSettingsService.filters(**data)
            message = "SupportSettings fetched successfully"

        case "PUT":
            result, status_code = await SupportSettingsService.update(**data)
            message = "SupportSettings updated successfully"

        case "DELETE":
            result, status_code = await SupportSettingsService.delete(**data)
            message = "SupportSettings deleted successfully"

        case _:
            return APIResponse.error(message="Method not allowed", code=405)

    return APIResponse.success(data=result, message=message, code=status_code)


# ========================== AGENTS CONTROLLER ==========================

async def agents_controller(request: Request, outlet_id: Optional[int] = None) -> ApiResponse:
    data = await get_request_data(request.headers.get("content-type", ""), request)
    
    if outlet_id:
        data.update({"outlet_id": outlet_id})
    
    method = request.method

    match method:
        case "POST":
            result, status_code = await AgentService.save(**data)
            message = "Agent created successfully"

        case "GET":
            result, status_code = await AgentService.get_auth_paginated_agents(**data)
            message = "Agents fetched successfully"

        case "PUT":
            result, status_code = await AgentService.update(**data)
            message = "Agent updated successfully"

        case "DELETE":
            result, status_code = await AgentService.delete(**data)
            if status_code == 200:
                message = "Agent deleted successfully"
            else:
                return APIResponse.error(message=result.get("error", "Agent deletion failed"), code=status_code)

        case _:
            return APIResponse.error(message="Method not allowed", code=405)

    return APIResponse.success(data=result, message=message, code=status_code)

async def agents_stats_controller(request: Request, outlet_id: Optional[int]) -> ApiResponse:
    data = await get_request_data(request.headers.get("content-type", ""), request)
    
    method = request.method
    if method != "GET":
        return APIResponse.error("Method not allowed", code=405)
    
    result, status_code = await AgentService.get_agent_stats(**data)
    message = "Agent stats fetched successfully"
    
    return APIResponse.success(data=result, message=message, code=status_code)


# ========================== TICKET RATING CONTROLLERS ==========================

async def agent_rating_controller(request: Request, outlet_id: Optional[int] = None) -> ApiResponse:
    data = await get_request_data(request.headers.get("content-type", ""), request)
    data["outlet_id"] = outlet_id
    
    result, status_code = await AuthTicketService.rate_ticket(**data)
    
    if status_code == 200:
        message = "Rating submitted successfully"
    else:
        message = result.get("error", "Rating failed")
    
    return APIResponse.success(data=result, message=message, code=status_code)

# async def customer_rating_controller(request: Request) -> ApiResponse:
#     data = await get_request_data(request.headers.get("content-type", ""), request)
    
#     result, status_code = await TicketService.rate_ticket(**data)
    
#     if status_code == 200:
#         message = "Rating submitted successfully"
#     else:
#         message = result.get("error", "Rating failed")
    
#     return APIResponse.success(data=result, message=message, code=status_code)