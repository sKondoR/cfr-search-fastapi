from typing import List

import traceback
import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.db import get_db
from app.api.models import Event
from app.core.config import settings
from app.core.constants import LIVE_RESULTS_BASE_URL, LIVE_RESULTS_PATH, EVENT_NAME, EVENT_YEAR, EVENT_GROUP

commandsRouter = APIRouter(prefix="/api", tags=["commands"])

@commandsRouter.get(
    "/commands",
    summary="Get commands",
    operation_id="get_commands",
    description=(
        "Get commands from the specified event by parsing the live results page. "
        "Finds the event 'Первенство России' with year 2025 and group 'v13', "
        "then fetches and parses the live results page to extract team names."
    ),
    dependencies=[], # Depends(PermissionCheck())
)
async def get_commands(db: AsyncSession = Depends(get_db)):
    # Find the event with name EVENT_NAME and year EVENT_YEAR in groups [EVENT_GROUP]
    query = select(Event).where(Event.name == EVENT_NAME).where(Event.year == EVENT_YEAR)
    result = await db.execute(query)
    events = result.scalars().all()
    
    # Filter events by group EVENT_GROUP
    filtered_events = [event for event in events if EVENT_GROUP in event.groups]
    
    if not filtered_events:
        raise HTTPException(status_code=404, detail=f"Event '{EVENT_NAME}' with group '{EVENT_GROUP}' and year {EVENT_YEAR} not found")
    
    # Take the first matching event
    event = filtered_events[0]
    
    # Construct the URL for live results
    url = f"{LIVE_RESULTS_BASE_URL}{event.link}/{LIVE_RESULTS_PATH}"
    
    try:
        # Make GET request to the live results page
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find all td elements with class "Команда" (Team)
        team_elements = soup.find_all("td", class_="Команда")
        
        # Extract text from each element
        teams = [elem.get_text(strip=True) for elem in team_elements]
        
        return {"teams": teams, "event": event.name}
        
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching live results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch live results: {str(e)}")
    except Exception as e:
        print(f"Error parsing live results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse live results: {str(e)}")