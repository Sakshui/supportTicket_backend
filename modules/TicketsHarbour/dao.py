from sqlalchemy import text, or_, select, bindparam
from .models import *
from.schemas import *
from app.database import *
from typing import Tuple
from app.database import SupportTicketAsyncSession
from sqlalchemy import func

JSON_KEY_MAPPING = {
    "email": "raised_by",
    "user_id": "raised_by",
    "user_type": "raised_by",
    "name": "raised_by",

    "customer_id": "customer_details",
    "customer_name": "customer_details",
    "customer_email": "customer_details",

    "priority": "additional_details",
    "department": "additional_details",
    "tags": "additional_details",
}

# -------------------------------------------------------------- TickitsHarbour ------------------------------------------------------------

class TicketsDao:

    @staticmethod
    async def create(ticket: TicketBase) -> int:
        ticket_obj = Ticket(**ticket.dict())
        return await create(ticket_obj)
    
    @staticmethod
    async def get_by_support_ticket_id(support_ticket_id: String) -> Optional[Ticket]:
        query = select(Ticket).where(Ticket.support_ticket_id== support_ticket_id)
        return await fetch_one(query)
    
    @staticmethod
    async def get_by_id(id: int) -> Optional[Ticket]:
        query = select(Ticket).where(Ticket.id== id)
        return await fetch_one(query)
    
    @staticmethod
    async def filters(**filters) -> List[Ticket]:
        query = select(Ticket)
        conditions = [getattr(Ticket, key) == value for key, value in filters.items()]
        query = select(Ticket).where(*conditions)
        return await fetch_all(query)

    @staticmethod
    async def global_search(
        *,
        outlet_id: int,
        search: str,
    ):
        pattern = f"%{search}%"

        query = select(Ticket).where(
            Ticket.outlet_id == outlet_id,
            or_(
                Ticket.support_ticket_id.ilike(pattern),
                Ticket.customer_details["customer_name"].astext.ilike(pattern),
                Ticket.customer_details["customer_email"].astext.ilike(pattern),
                Ticket.content["subject"].astext.ilike(pattern),
                Ticket.content["description"].astext.ilike(pattern),
            )
        )

        return await fetch_all(query)

    @staticmethod
    async def filters_auth(
        *,
        outlet_id: int | None,
        filters: dict,
    ) -> list[Ticket]:
        query = select(Ticket)
        conditions = []

        if outlet_id is not None:
            conditions.append(Ticket.outlet_id == outlet_id)

        ALLOWED_COLUMNS = {
            "support_ticket_id",
            "status",
            "assigned_agent",
            "is_in_trash",
        }

        for key, value in filters.items():
            if value is None:
                continue

            if key in ALLOWED_COLUMNS:
                conditions.append(getattr(Ticket, key) == value)
                continue

            json_column_name = JSON_KEY_MAPPING.get(key)
            if json_column_name:
                column = getattr(Ticket, json_column_name)

                conditions.append(column[key].astext == str(value))
                continue

            raise ValueError(f"Unsupported filter: {key}")

        if conditions:
            query = query.where(*conditions)

        return await fetch_all(query)

    @staticmethod
    async def filters_unauth(**filters) -> List[Ticket]:
        query = select(Ticket)
        conditions = []

        for key, value in filters.items():
            if hasattr(Ticket, key):
                conditions.append(getattr(Ticket, key) == value)
                continue
            
            json_field = JSON_KEY_MAPPING.get(key)
            if json_field:
                column = getattr(Ticket, json_field)
                conditions.append(column[key].astext == str(value))
                continue
        query = select(Ticket).where(*conditions)
        return await fetch_all(query)
    
    @staticmethod
    async def update(ticket: TicketUpdateIn) -> int:
        ticket = Ticket(**ticket.dict())
        return await update(ticket)
    
    @staticmethod
    async def delete(id: int):
        await delete_by_id(Ticket, id=id)

    @staticmethod
    async def get_last_ticket(outlet_id: int) -> Optional[str]:
        query = select(Ticket.support_ticket_id).where(Ticket.outlet_id == outlet_id).order_by(Ticket.id.desc()).limit(1)

        async with SupportTicketAsyncSession() as session:
            result = await session.execute(query)
            row = result.scalar_one_or_none()

            if row is None:
                return None
            return str(row)     


    @staticmethod
    async def update_status_and_agent(ticket_update: TicketUpdateIn):
        """
        Update ticket using TicketUpdateIn typehint.
        Sets closed_at timestamp when status changes to 'close'.
        """
        status_value = ticket_update.status.value.lower() if hasattr(ticket_update.status, 'value') else str(ticket_update.status).lower()
        
        # Set closed_at if status is being changed to 'close'
        if status_value == 'close':
            query = text("""
                UPDATE tickets
                SET 
                    status = :status,
                    assigned_agent = :assigned_agent,
                    updated_at = NOW(),
                    closed_at = CASE 
                        WHEN closed_at IS NULL THEN NOW()
                        ELSE closed_at
                    END
                WHERE id = :id AND outlet_id = :outlet_id
                RETURNING id;
            """)
        else:
            query = text("""
                UPDATE tickets
                SET 
                    status = :status,
                    assigned_agent = :assigned_agent,
                    updated_at = NOW()
                WHERE id = :id AND outlet_id = :outlet_id
                RETURNING id;
            """)
        
        query = query.bindparams(
            id=ticket_update.id,
            outlet_id=ticket_update.outlet_id,
            status=status_value,
            assigned_agent=ticket_update.assigned_agent
        )

        result = await execute_query(query)
        row = result.fetchone()
        return row[0] if row else None

    @staticmethod
    async def get_outlet(shop: str) -> Tuple[str, str]:
        query = text(""" SELECT * FROM shopify_shop WHERE shop = :shop """).bindparams( shop= shop)
        result = await fetch_one(query)
        if not result:
            raise ValueError("No outlet info found")
        return result
    
    @staticmethod
    async def count_open_tickets_by_agent(agent_id: int) -> int:
        query = select(func.count(Ticket.id)).where(Ticket.assigned_agent == agent_id, Ticket.status != 'close')
        return await fetch_one(query)
    
    @staticmethod
    async def update_agent_rating(id: int, rating: int):
        query = text("""
                UPDATE tickets
                SET 
                    agent_rating = :rating,
                    updated_at = NOW()
                WHERE id = :id
                RETURNING id;
            """).bindparams(id=id, rating=rating)
        
        result = await execute_query(query)
        row = result.fetchone()
        return row[0] if row else None

    @staticmethod
    async def update_customer_rating(ticket_id: int, rating: int):
        async with SupportTicketAsyncSession() as session:
            query = text("""
                UPDATE tickets
                SET 
                    customer_rating = :rating,
                    updated_at = NOW()
                WHERE id = :id
                RETURNING id;
            """).bindparams(id=ticket_id, rating=rating)
        
        result = await execute_query(query)
        row = result.fetchone()
        return row[0] if row else None
        
        
# -------------------------------------------------------------- SupportSettings ------------------------------------------------------------

class SupportSettingsDao:

    @staticmethod
    async def create(setting: SupportSettingsBase) -> int:
        setting = SupportSettings(**setting.dict())
        return await create(setting)
    
    @staticmethod
    async def get_by_outlet_id_or_web_url(outlet_id: Optional[int]=None, web_url: Optional[str]=None) -> Optional[SupportSettings]:
        if outlet_id:
            query = select(SupportSettings).where(SupportSettings.outlet_id == outlet_id)
        else:
            query = select(SupportSettings).where(SupportSettings.web_url == web_url)
        return await fetch_one(query)

    @staticmethod
    async def get_by_api_key(api_key: str) -> Optional[SupportSettings]:
        query = select(SupportSettings).where(
            SupportSettings.api_key == api_key
        )
        return await fetch_one(query)
    
    @staticmethod
    async def get_outlet_by_web_url(web_url: str)-> int:
        query = select(SupportSettings.outlet_id).where(SupportSettings.web_url == web_url)
        
        outlet_id = await fetch_one(query)
        if not outlet_id:
            raise ValueError(f"No outlet found for web_url: {web_url}")
        return outlet_id
    
    @staticmethod
    async def filters(**filters) -> List[SupportSettings]:
        query = select(SupportSettings)
        conditions = [getattr(SupportSettings, key) == value for key, value in filters.items()]
        query = select(SupportSettings).where(*conditions)
        return await fetch_all(query)
    
    @staticmethod
    async def update(setting: SupportSettingsUpdateIn) -> int:
        setting = SupportSettings(**setting.dict())
        return await update(setting)
    
    @staticmethod
    async def delete(id: int):
        await delete_by_id(SupportSettings, id=id)

    @staticmethod
    async def get_outlet_by_api_key(api_key: str):
        query = text("""
            SELECT outlet_id
            FROM shopify_shop
            WHERE api_key = :api_key
        """).bindparams(api_key=api_key)

        result = await fetch_one(query)

        if not result:
            raise ValueError("Invalid API Key")

        return result


# -------------------------------------------------------------- Agents ------------------------------------------------------------

class AgentsDao:

    @staticmethod
    async def create(agent: AgentBase) -> int:
        agent_obj = Agent(**agent.dict())
        return await create(agent_obj)
    
    @staticmethod
    async def get_by_id(id: int) -> Optional[Agent]:
        query = select(Agent).where(Agent.id == id)
        return await fetch_one(query)
    
    @staticmethod
    async def get_by_user_id(user_id: int) -> Optional[Agent]:
        query = select(Agent).where(Agent.user_id == user_id)
        return await fetch_one(query)
    
    @staticmethod
    async def filters(**filters) -> List[Agent]:
        query = select(Agent)
        conditions = [getattr(Agent, key) == value for key, value in filters.items()]
        query = select(Agent).where(*conditions)
        return await fetch_all(query)
    
    @staticmethod
    async def update(agent: AgentUpdateIn) -> int:
        agent_obj = Agent(**agent.dict())
        return await update(agent_obj)
    
    @staticmethod
    async def delete(id: int):
        await delete_by_id(Agent, id=id)
