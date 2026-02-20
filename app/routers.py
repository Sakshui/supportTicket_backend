from fastapi import FastAPI
from modules.TicketsHarbour.routers import router as ticket_harbour
from modules.AnalyticsHarbour.routers import router as analytics_harbour
from modules.ShopifyHarbour.routers import router as shopify_harbour


def routers(app: FastAPI):
    app.include_router(ticket_harbour, prefix="/api/v1/ticket", tags=["ticket"])
    app.include_router(analytics_harbour, prefix="/api/v1/analytics", tags=["analytics"])
    app.include_router(shopify_harbour, prefix="/api/v1/analytics", tags=["shopify"])
