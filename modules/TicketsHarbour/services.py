from .schemas import *
from .dao import *
from math import ceil

class AuthTicketService:
    
    @staticmethod
    async def save(**data):

        outlet_id = data.get('outlet_id')
        support_settings_for_outlet = await SupportSettingsDao.get_by_outlet_id_or_web_url(outlet_id=outlet_id)
        
        if not support_settings_for_outlet:
            return {"error": "SupportSettings not found for Outlet"}, 404


        department = data.get("department")
        if not department:
            return {"error": "department field is required"}, 400

        settings = support_settings_for_outlet.settings
        ticket_prefix = settings["prefix"]
        start_no = settings["start_no"]
        email_required = settings["email_required"]
        # email = data.get("raised_by", {}).get("email")
        
        raised_by = data.get("raised_by")
        raised_by_id = data.get("raised_by_id")
        if email_required and raised_by is None and raised_by_id is None:
            return {"error": "Kindly provide email and other required fields to generate Ticket."}, 400
        if raised_by is not None:
            if raised_by != TicketRaisedByEnum.AGENT.value and raised_by != TicketRaisedByEnum.CUSTOMER.value:
                return {"error": "Ticket raiser should be valid entity - customer or agent."}, 400

        last_ticket = await TicketsDao.get_last_ticket(outlet_id=outlet_id)
        if last_ticket:
            current_no = ''.join(ch for ch in last_ticket if ch.isdigit())
            next_no = int(current_no) + 1
        else:
            next_no = int(start_no)

        padded_no = str(next_no).zfill(3)
        support_ticket_id = f"{ticket_prefix}{padded_no}"

        data.update({"support_ticket_id": support_ticket_id})

        ticket_model = TicketBase(**data)
        id_ = await TicketsDao.create(ticket_model)
        return {"id": id_}, 200

    @staticmethod
    async def get_by_support_ticket_id(support_ticket_id: str):
        ticket = await TicketsDao.get_by_support_ticket_id(support_ticket_id)
        if not ticket:
            return {"ticket": None}, 404

        ticket = TicketRead.from_orm(ticket).model_dump()
        return {"ticket": ticket}, 200

    @staticmethod
    async def get_support_tickets_by_assigned_agent(agent_id: int):
        tickets = await TicketsDao.get_by_assigned_agent_id(agent_id)
        if not tickets:
            return {"tickets": []}, 404

        agent_tickets = [
                TicketRead.model_validate(ticket).model_dump()
                for ticket in tickets
            ]
        return {"tickets" : agent_tickets}, 200

    @staticmethod
    async def global_search(*, outlet_id: int,search: str,):
        if len(search) < 2:
            return {"tickets": []}, 200

        tickets = await TicketsDao.global_search(outlet_id=outlet_id, search=search, )

        tickets = [TicketRead.from_orm(t).model_dump() for t in tickets]

        return {"tickets": tickets}, 200

    @staticmethod
    async def filters(**filters):
        tickets = await TicketsDao.filters(**filters)
        tickets = [TicketRead.from_orm(t).model_dump() for t in tickets]
        print("[SERVICE] Tickets successfully fetched")
        return {"tickets": tickets}, 200

    @staticmethod
    async def filters_auth(*, outlet_id: int, filters: dict):
        """
        Filters tickets for authenticated users.
        Enforces outlet-level scoping.
        """

        tickets = await TicketsDao.filters_auth(outlet_id=outlet_id, filters=filters,)
        tickets = [TicketRead.from_orm(t).model_dump() for t in tickets]

        return {"tickets": tickets}, 200

    @staticmethod
    async def delete(**data):
        ticket_id = data.get("id")
        if not ticket_id:
            return {"error": "id is required for delete"}, 400

        await TicketsDao.delete(ticket_id)
        return {"id": ticket_id}, 200

    @staticmethod
    async def update(**data):
        ticket_id = data.get("id")
        status = data.get("status")
        assigned_agent_id = data.get("assigned_agent_id")
        outlet_id = data.get('outlet_id')

        if assigned_agent_id is not None:
            agent = await AgentsDao.get_by_id(assigned_agent_id)
            if not agent:
                return {"error": "Assigned agent not found"}, 400

            if agent.outlet_id != outlet_id:
                return {"error": "Agent does not belong to this outlet"}, 403

            if agent.status != "active":
                return {"error": "Agent is not active"}, 400

        ticket_update = TicketUpdateIn(id = ticket_id, outlet_id=outlet_id, status=status, assigned_agent_id=assigned_agent_id)
        # print("Ticket Update Payload: ", ticket_update)
        
        updated_id = await TicketsDao.update_status_and_agent(ticket_update)

        return {"id": updated_id}, 200

    @staticmethod
    async def rate_ticket(**data):
        ticket_id = data.get("id")
        rating = data.get("rating")
        
        if not ticket_id or rating is None:
            return {"error": "id and rating are required"}, 400
        
        ticket = await TicketsDao.get_by_id(ticket_id)
        if not ticket:
            return {"error": "Ticket not found"}, 404
        
        if ticket.status != "closed":
            return {"error": "Can only rate closed tickets"}, 400
        
        rating_model = TicketRatingIn(id=ticket_id, rating=rating)
        
        id_ = await TicketsDao.update_customer_rating(ticket_id, rating_model.rating)
        return {"id": id_, "rating": rating_model.rating}, 200


    @staticmethod
    async def get_auth_paginated_tickets(**data):

        outlet_id = data.get("outlet_id")

        # Pagination
        page = max(int(data.get("page", 1)), 1)
        page_size = int(data.get("page_size", 10))

        limit = page_size
        offset = (page - 1) * limit

        # Optional params
        search = data.get("search")

        sort_by = data.get("sort_by") or "created_at"
        sort_order = data.get("sort_order") or "desc"

        filters = {
            "status": data.get("status"),
            "priority": data.get("priority"),
            "department": data.get("department"),
        }

        filters = {k: v for k, v in filters.items() if v is not None}

        tickets, total_ticket_count = await TicketsDao.get_paginated_tickets(
            outlet_id=outlet_id,
            limit=limit,
            offset=offset,
            search=search,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        tickets = [TicketRead.from_orm(t).model_dump() for t in tickets]

        if (page_size != 0):
            total_pages = ceil(total_ticket_count[0] / page_size)
            has_next = page < total_pages
            has_previous = page > 1
            page_start = offset + 1
        else:
            total_pages = 1
            has_next = False
            has_previous = False
            page_start = 1
        
        page_end = min(offset + page_size, total_ticket_count[0])

        return {"tickets": tickets, 
                "page": page, 
                "page_size": page_size, 
                "page_content_size": len(tickets), 
                "total_tickets": total_ticket_count[0],
                "total_pages": total_pages,
                "page_start": page_start,
                "page_end": page_end,
                "has_next": has_next,
                "has_previous": has_previous,
                }, 200 

    @staticmethod
    async def get_ticket_stats(**data):
        
        outlet_id = data.get("outlet_id")
        
        if outlet_id is not None:
            outlet_id = int(outlet_id)
        
        ticket_stats = await TicketsDao.get_ticket_stats(outlet_id=outlet_id)
        
        return {"ticket_stats": ticket_stats}, 200


class TicketService:

    @staticmethod
    async def save(**data):

        web_url = data.get('web_url')
        support_settings_for_outlet = await SupportSettingsDao.get_by_outlet_id_or_web_url(web_url=web_url)

        if not support_settings_for_outlet:
            return {"error": f"SupportSettings not found for shop '{web_url}'"}, 404

        data["outlet_id"] = support_settings_for_outlet.outlet_id

        additional = data.get("additional_details", {})
        if not additional or "department" not in additional:
            return {"error": "department field is required"}, 400

        outlet_id = data["outlet_id"]
        support_settings_for_outlet = await SupportSettingsDao.get_by_outlet_id_or_web_url(outlet_id=outlet_id)
        settings = support_settings_for_outlet.settings

        ticket_prefix = settings["prefix"]
        start_no = settings["start_no"]
        email_required = settings["email_required"]
        email = data.get("raised_by", {}).get("email")

        if email_required and email is None:
            return {"error": "kindly provide email to generate Ticket."}, 400

        # ---- Generate ticket number ----
        last_ticket = await TicketsDao.get_last_ticket(outlet_id=outlet_id)
        if last_ticket:
            current_no = ''.join(ch for ch in last_ticket if ch.isdigit())
            next_no = int(current_no) + 1
        else:
            next_no = int(start_no)

        padded_no = str(next_no).zfill(3)
        support_ticket_id = f"{ticket_prefix}{padded_no}"

        data["support_ticket_id"] = support_ticket_id

        department = additional.get("department")
        department_agents = await AgentsDao.filters(outlet_id=outlet_id, department=department)

        if not department_agents:
            return {"error": f"No agents found for department '{department}'"}, 400
        
        # Find agent with least open tickets, default to first agent
        lowest_load = -1
        selected_agent = department_agents[0]
        
        for agent in department_agents:
            open_ticket_count = await TicketsDao.count_open_tickets_by_agent(agent_id=agent.id)
            if open_ticket_count < lowest_load or lowest_load == -1:
                lowest_load = open_ticket_count
                selected_agent = agent

        data["assigned_agent"] = selected_agent.id

        ticket_model = TicketBase(**data)
        id_ = await TicketsDao.create(ticket_model)
        return {"id": id_}, 200
    
    @staticmethod
    async def filters(**filters):
        web_url = filters.get("web_url")
        outlet_id = await SupportSettingsDao.get_outlet_by_web_url(web_url=web_url)
        filters.pop("web_url")
        filters["outlet_id"] = outlet_id

        tickets = await TicketsDao.filters_unauth(**filters)
        tickets = [TicketRead.from_orm(ticket).dict() for ticket in tickets]
        return {"tickets": tickets}, 200


    @staticmethod
    async def delete(**data):
        id_ = data.get('id')
        if not id_:
            raise ValueError("Missing 'id' to delete ticket")
        ticket = await TicketsDao.get_by_id(id=id_)
        if not ticket:
            return {"ticket": None}, 404
        
        customer_id = data.get("customer_id")
        ticket_customer_id = (ticket.customer_details or {}).get("customer_id")

        if int(customer_id) == int(ticket_customer_id):
            await TicketsDao.delete(id=id_)
            return {"id": id_}, 200
        else:
            return {"id":None}, 403
        
    @staticmethod
    async def rate_ticket(**data):
        ticket_id = data.get("id")
        rating = data.get("rating")
        
        if not ticket_id or rating is None:
            return {"error": "id and rating are required"}, 400
        
        ticket = await TicketsDao.get_by_id(ticket_id)
        if not ticket:
            return {"error": "Ticket not found"}, 404
        
        if ticket.status != "closed":
            return {"error": "Can only rate closed tickets"}, 400
        
        rating_model = TicketRatingIn(id=ticket_id, rating=rating)
        
        id_ = await TicketsDao.update_agent_rating(ticket_id, rating_model.rating)
        return {"id": id_, "rating": rating_model.rating}, 200


class SupportSettingsService:

    @staticmethod
    async def save(**data):
        outlet_id = data.get("outlet_id")
        existing = await SupportSettingsDao.get_by_outlet_id_or_web_url(outlet_id=outlet_id)

        if existing:
            data["id"] = existing.id
            id_ = await SupportSettingsDao.update(SupportSettingsUpdateIn(**data))
            return {"id": id_}, 200

        model = SupportSettingsBase(**data)
        id_ = await SupportSettingsDao.create(model)
        return {"id": id_}, 200

    @staticmethod
    async def filters(**filters):
        settings = await SupportSettingsDao.filters(**filters)
        settings = [SupportSettingsRead.from_orm(i).model_dump() for i in settings]
        return {"settings": settings}, 200

    @staticmethod
    async def update(**data):
        id_ = await SupportSettingsDao.update(SupportSettingsUpdateIn(**data))
        return {"id": id_}, 200

    @staticmethod
    async def delete(**data):
        id_ = data.get("id")
        if not id_:
            raise ValueError("Missing id for deletion")

        await SupportSettingsDao.delete(id=id_)
        return {"id": id_}, 200


class AgentService:

    @staticmethod
    async def save(**data):
        user_id = data.get("user_id")
        if not user_id:
            return {"error": "Missing user id"}, 400

        existing = await AgentsDao.get_by_user_id(user_id=user_id)
        if existing:
            return {"error": "User has already been designated as an agent"}, 409

        # Add validation for required fields
        if not data.get("category") or not data.get("sub_category"):
            return {"error": "Category and sub_category are required"}, 400

        agent_model = AgentBase(**data)
        id_ = await AgentsDao.create(agent_model)
        return {"id": id_}, 200

    @staticmethod
    async def get_by_id(agent_id: int):
        agent = await AgentsDao.get_by_id(agent_id)
        if not agent:
            return {"agent": None}, 404

        agent = AgentRead.from_orm(agent).model_dump()
        return {"agent": agent}, 200

    @staticmethod
    async def get_by_user_id(user_id: int):
        agent = await AgentsDao.get_by_user_id(user_id)
        if not agent:
            return {"agent": None}, 404

        agent = AgentRead.from_orm(agent).model_dump()
        return {"agent": agent}, 200

    @staticmethod
    async def filters(**filters):
        agents = await AgentsDao.filters(**filters)
        agents = [AgentRead.from_orm(agent).model_dump() for agent in agents]
        return {"agents": agents}, 200

    @staticmethod
    async def update(**data):
        agent_id = data.get("id")
        if not agent_id:
            return {"error": "id is required for update"}, 400

        # Verify agent exists
        existing = await AgentsDao.get_by_id(agent_id)
        if not existing:
            return {"error": "Agent not found"}, 404

        agent_update = AgentUpdateIn(**data)
        id_ = await AgentsDao.update(agent_update)
        return {"id": id_}, 200

    @staticmethod
    async def delete(**data):
        agent_id = data.get("id")
        if not agent_id:
            return {"error": "id is required for delete"}, 400

        # Verify agent exists
        existing = await AgentsDao.get_by_id(agent_id)
        if not existing:
            return {"error": "Agent not found"}, 404

        await AgentsDao.delete(agent_id)
        return {"id": agent_id}, 200
    
    @staticmethod
    async def get_auth_paginated_agents(**data):

        outlet_id = data.get("outlet_id")

        # Pagination
        page = max(int(data.get("page", 1)), 1)
        page_size = int(data.get("page_size", 10))

        limit = page_size
        offset = (page - 1) * limit

        # Optional params
        search = data.get("search")

        sort_by = data.get("sort_by") or "created_at"
        sort_order = data.get("sort_order") or "desc"

        filters = {
            "status": data.get("status"),
            "level": data.get("level"),
            "department": data.get("department"),
        }

        filters = {k: v for k, v in filters.items() if v is not None}

        agents, total_agent_count = await AgentsDao.get_paginated_agents(
            outlet_id=outlet_id,
            limit=limit,
            offset=offset,
            search=search,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        agents = [AgentRead.from_orm(t).model_dump() for t in agents]

        if (page_size != 0):
            total_pages = ceil(total_agent_count[0] / page_size)
            has_next = page < total_pages
            has_previous = page > 1
            page_start = offset + 1
        else:
            total_pages = 1
            has_next = False
            has_previous = False
            page_start = 1
        
        page_end = min(offset + page_size, total_agent_count[0])

        return {"agents": agents, 
                "page": page, 
                "page_size": page_size, 
                "page_content_size": len(agents), 
                "total_agents": total_agent_count[0],
                "total_pages": total_pages,
                "page_start": page_start,
                "page_end": page_end,
                "has_next": has_next,
                "has_previous": has_previous,
                }, 200 
    
    @staticmethod
    async def get_agent_stats(**data):
        
        outlet_id = data.get("outlet_id")
        
        if outlet_id is not None:
            outlet_id = int(outlet_id)
        
        agent_stats = await AgentsDao.get_agent_stats(outlet_id=outlet_id)
        
        return {"agent_stats": agent_stats}, 200
