"""Hemisphere API client."""
import logging
from typing import Any, Dict, Optional

import aiohttp
import async_timeout
import asyncio

from .const import (
    HEMISPHERE_SIGNIN_URL,
    HEMISPHERE_BUILDINGS_URL,
    HEMISPHERE_URL,
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
        """Authenticate with hemisphere API."""
        try:
            _LOGGER.debug("Authenticating with Hemisphere API")
            
            # Retry authentication up to 3 times
            for retry in range(3):
                try:
                    # Authenticate with Hemisphere API
                    async with self.session.post(
                        f"{HEMISPHERE_URL}{HEMISPHERE_SIGNIN_URL}",
                        json={"email": username, "password": password},
                        headers={"Content-Type": "application/json"},
                        timeout=30  # Increase timeout
                    ) as response:
                        if response.status != 200:
                            _LOGGER.error(
                                "Failed to authenticate with Hemisphere API: %s %s",
                                response.status,
                                response.reason,
                            )
                            if retry < 2:  # Try again if we have retries left
                                wait_time = (retry + 1) * 5
                                _LOGGER.warning(
                                    "Authentication failed, retrying in %s seconds (attempt %s/3)",
                                    wait_time,
                                    retry + 1
                                )
                                await asyncio.sleep(wait_time)
                                continue
                            return False
                            
                        data = await response.json()
                        self.hemisphere_token = data.get("token")
                        
                        if not self.hemisphere_token:
                            _LOGGER.error("No token in response")
                            return False
                            
                        # Token is valid, now get buildings info
                        return await self._get_buildings_info()
                        
                except (aiohttp.ClientError, asyncio.TimeoutError) as err:
                    _LOGGER.error("Error in authentication request: %s", err)
                    if retry < 2:  # Try again if we have retries left
                        wait_time = (retry + 1) * 5
                        await asyncio.sleep(wait_time)
                        continue
                    return False
                    
            return False  # All retries failed
                
        except Exception as err:
            _LOGGER.error("Unexpected error in authentication: %s", err, exc_info=True)
            return False

    async def _get_buildings_info(self) -> bool:
        """Get building info."""
        try:
            # Retry getting building info up to 3 times
            for retry in range(3):
                try:
                    # Get buildings info
                    async with self.session.get(
                        f"{HEMISPHERE_URL}{HEMISPHERE_BUILDINGS_URL}",
                        headers={"Authorization": f"Bearer {self.hemisphere_token}"},
                        timeout=30  # Increased timeout
                    ) as response:
                        if response.status != 200:
                            _LOGGER.error(
                                "Failed to get building info: %s %s",
                                response.status,
                                response.reason,
                            )
                            if retry < 2:  # Try again if we have retries left
                                wait_time = (retry + 1) * 5
                                _LOGGER.warning(
                                    "Failed to get building info, retrying in %s seconds (attempt %s/3)",
                                    wait_time,
                                    retry + 1
                                )
                                await asyncio.sleep(wait_time)
                                continue
                            return False
                            
                        data = await response.json()
                        
                        # Extract building info
                        if not data:
                            _LOGGER.error("No buildings in response")
                            return False
                            
                        building = data[0]
                        self.building_id = building.get("buildingId")
                        self.hemis_base_url = building.get("hemis_base_url")
                        self.hemis_stomp_url = building.get("hemis_stomp_url")
                        
                        if not self.building_id or not self.hemis_base_url or not self.hemis_stomp_url:
                            _LOGGER.error(
                                "Missing required building info: building_id=%s, hemis_base_url=%s, hemis_stomp_url=%s",
                                self.building_id,
                                self.hemis_base_url,
                                self.hemis_stomp_url
                            )
                            return False
                            
                        # Log the URLs for debugging
                        _LOGGER.debug("Hemisphere token: %s...", self.hemisphere_token[:10])
                        _LOGGER.debug("Building ID: %s", self.building_id)
                        _LOGGER.debug("Hemis base URL: %s", self.hemis_base_url)
                        _LOGGER.debug("Hemis STOMP URL: %s", self.hemis_stomp_url)
                        
                        return True
                        
                except (aiohttp.ClientError, asyncio.TimeoutError) as err:
                    _LOGGER.error("Error getting building info: %s", err)
                    if retry < 2:  # Try again if we have retries left
                        wait_time = (retry + 1) * 5
                        await asyncio.sleep(wait_time)
                        continue
                    return False
                    
            return False  # All retries failed
            
        except Exception as err:
            _LOGGER.error("Unexpected error getting building info: %s", err, exc_info=True)
            return False
