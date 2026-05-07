"""API v1 routes."""

# Import routers directly from their modules to avoid circular imports
from app.api.v1.endpoints.events import events_router as events
from app.api.v1.endpoints.teams import teams_router as teams

__all__ = ["events", "teams"]
