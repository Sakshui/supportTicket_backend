# XIRCLS Support Ticket System

## Changelog

### December 21

- Added Agent functionality to these files:
  - **models.py**: `Agent` class
  - **schemas.py**: `LevelEnum`, `AgentBase`, `AgentRead`, `AgentUpdateIn` classes
  - **dao.py**: `AgentsDao` class
  - **controller.py**: `agents_controller` function
- Added agent assignment to `TicketService.save` method in **services.py**
- Added `agent_rating` and `customer_rating` fields to `Ticket` class
- Added `TicketRatingIn` schema to validate rating
- Added `update_agent_rating` and `update_customer_rating` methods to `TicketsDao`
- Added `rate_ticket` to `services.py`
- Added `agent_rating_controller` and `customer_rating_controller` to `controller.py`

## Current Tasks

- Set up PyMongo with MongoDB
- Test thoroughly for errors with the tickets and agents APIs
- Ensure that all of this functionality is complete and bug-free ASAP:
  - Create support ticket
  - View ticket
  - Change ticket status (done by agent)
  - Assign agent (done automatically or by merchant)
  - Select customer on support ticket creation (done by agent)
- Work on message functionality (may take longer)
