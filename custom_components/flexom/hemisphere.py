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
        self.hemis_token: Optional[str] = None

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
                        
                        # Log the entire building info for diagnostic
                        _LOGGER.debug("Building info: %s", building)
                        
                        self.building_id = building.get("buildingId")
                        
                        # Check for direct URLs first
                        self.hemis_base_url = building.get("hemis_base_url")
                        self.hemis_stomp_url = building.get("hemis_stomp_url")
                        
                        # If direct URLs aren't provided, try to construct them
                        if not self.hemis_base_url or not self.hemis_stomp_url:
                            # Try to extract region from hemis_url if it exists
                            hemis_url = building.get("hemis_url", "")
                            region = "eu-west"  # default
                            
                            # Extract region from URL if possible
                            if "eu-central" in hemis_url:
                                region = "eu-central"
                            elif "eu-west" in hemis_url:
                                region = "eu-west"
                                
                            # Try to extract instance name
                            instance_name = None
                            if hemis_url:
                                try:
                                    # URL format is typically https://instance-name.region.hemis.io/
                                    parts = hemis_url.split("//")[1].split(".")[0]
                                    instance_name = parts
                                except (IndexError, AttributeError):
                                    _LOGGER.warning("Could not extract instance name from %s", hemis_url)
                            
                            # If we don't have an instance name, try to extract from STOMP URL
                            if not instance_name and self.hemis_stomp_url:
                                try:
                                    instance_name = self.hemis_stomp_url.split("//")[1].split("-stomp")[0]
                                except (IndexError, AttributeError):
                                    _LOGGER.warning("Could not extract instance name from STOMP URL %s", self.hemis_stomp_url)
                            
                            # Construct URLs if needed
                            if not self.hemis_base_url:
                                if instance_name:
                                    self.hemis_base_url = f"https://{instance_name}.{region}.hemis.io/hemis/rest"
                                else:
                                    self.hemis_base_url = f"https://{self.building_id}.{region}.hemis.io/hemis/rest"
                                _LOGGER.warning("Constructed Hemis base URL: %s", self.hemis_base_url)
                                
                            if not self.hemis_stomp_url:
                                if instance_name:
                                    self.hemis_stomp_url = f"wss://{instance_name}-stomp.{region}.hemis.io"
                                else:
                                    self.hemis_stomp_url = f"wss://{self.building_id}-stomp.{region}.hemis.io"
                                _LOGGER.warning("Constructed Hemis STOMP URL: %s", self.hemis_stomp_url)
                        
                        if not self.building_id or not self.hemis_base_url or not self.hemis_stomp_url:
                            _LOGGER.error(
                                "Missing required building info: building_id=%s, hemis_base_url=%s, hemis_stomp_url=%s",
                                self.building_id,
                                self.hemis_base_url,
                                self.hemis_stomp_url
                            )
                            return False
                            
                        # Get the Hemis token - this is the key for API access
                        self.hemis_token = building.get("hemis_token")
                        if self.hemis_token:
                            _LOGGER.debug("Got Hemis token: %s...", self.hemis_token[:10])
                        else:
                            _LOGGER.warning("No Hemis token in building info, API calls may fail")
                            # We'll keep using the Hemisphere token, but it might not work
                            self.hemis_token = self.hemisphere_token
                        
                        # Log the URLs for debugging
                        _LOGGER.debug("Hemisphere token: %s...", self.hemisphere_token[:10])
                        _LOGGER.debug("Hemis token: %s...", self.hemis_token[:10] if self.hemis_token else "None")
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
