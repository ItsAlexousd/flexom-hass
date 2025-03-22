"""Hemisphere API client."""
import logging
from typing import Any, Dict, Optional

import aiohttp
import async_timeout

from .const import (
    HEMISPHERE_SIGNIN_URL,
    HEMISPHERE_BUILDINGS_URL,
)

_LOGGER = logging.getLogger(__name__)


class HemisphereApiClient:
    """Client for interacting with the Hemisphere API."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self.session = session
        self.hemisphere_token: Optional[str] = None
        self.building_id: Optional[str] = None
        self.hemis_base_url: Optional[str] = None
        self.hemis_stomp_url: Optional[str] = None

    async def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with the Hemisphere API and retrieve building info."""
        if not await self._fetch_hemisphere_token(username, password):
            return False
        
        return await self._fetch_building_info()

    async def _fetch_hemisphere_token(self, username: str, password: str) -> bool:
        """Authenticate with the Hemisphere API."""
        try:
            async with async_timeout.timeout(10):
                response = await self.session.post(
                    HEMISPHERE_SIGNIN_URL,
                    json={"email": username, "password": password},
                    headers={"Content-Type": "application/json"},
                )
                
                if response.status != 200:
                    _LOGGER.error(
                        "Failed to authenticate with Hemisphere: %s", 
                        response.status
                    )
                    return False
                
                data = await response.json()
                self.hemisphere_token = data.get("token")
                
                if not self.hemisphere_token:
                    _LOGGER.error("No token found in Hemisphere response")
                    return False
                
                return True
                
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to Hemisphere API: %s", err)
            return False
        except async_timeout.TimeoutError:
            _LOGGER.error("Timeout connecting to Hemisphere API")
            return False

    async def _fetch_building_info(self) -> bool:
        """Fetch building information from Hemisphere."""
        if not self.hemisphere_token:
            _LOGGER.error("No Hemisphere token available")
            return False
            
        try:
            async with async_timeout.timeout(10):
                response = await self.session.get(
                    HEMISPHERE_BUILDINGS_URL,
                    headers={
                        "Authorization": f"Bearer {self.hemisphere_token}",
                        "Content-Type": "application/json",
                    },
                )
                
                if response.status != 200:
                    _LOGGER.error("Failed to fetch building info: %s", response.status)
                    return False
                    
                buildings = await response.json()
                
                if not buildings or not isinstance(buildings, list) or len(buildings) == 0:
                    _LOGGER.error("No buildings found in Hemisphere response")
                    return False
                
                # Use the first building
                building = buildings[0]
                self.building_id = building.get("buildingId")
                self.hemis_base_url = f"https://{self.building_id}.eu-west.hemis.io/hemis/rest"
                self.hemis_stomp_url = building.get("hemis_stomp_url")
                
                if not self.building_id or not self.hemis_stomp_url:
                    _LOGGER.error("Missing building ID or STOMP URL")
                    return False
                
                return True
                
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to Hemisphere API: %s", err)
            return False
        except async_timeout.TimeoutError:
            _LOGGER.error("Timeout connecting to Hemisphere API")
            return False
