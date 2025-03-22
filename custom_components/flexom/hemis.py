"""Hemis API client."""
import logging
from typing import Any, Dict, List, Optional

import aiohttp
import async_timeout

from .const import (
    FACTOR_BRIGHTNESS,
    FACTOR_BRIGHTNESS_EXT,
    FACTOR_TEMPERATURE,
)

_LOGGER = logging.getLogger(__name__)

class HemisApiClient:
    """Client for interacting with the Hemis API."""

    def __init__(
        self, 
        session: aiohttp.ClientSession, 
        hemis_base_url: str, 
        token: str
    ) -> None:
        """Initialize the API client."""
        self.session = session
        self.hemis_base_url = hemis_base_url
        self.token = token

    async def get_zones(self) -> List[Dict[str, Any]]:
        """Get all zones."""
        return await self._api_request("GET", "/zones")

    async def get_zone_factors(self, zone_id: str) -> List[Dict[str, Any]]:
        """Get all factors for a zone."""
        return await self._api_request("GET", f"/zones/{zone_id}/factors")

    async def get_sensors(self) -> List[Dict[str, Any]]:
        """Get all sensors."""
        return await self._api_request("GET", "/intelligent-things/sensors")

    async def get_actuators(self) -> List[Dict[str, Any]]:
        """Get all actuators."""
        return await self._api_request("GET", "/intelligent-things/actuators")

    async def get_light_actuators(self) -> List[Dict[str, Any]]:
        """Get all light actuators."""
        _LOGGER.debug("Fetching light actuators")
        actuators = await self.get_actuators()
        _LOGGER.debug("Found %d actuators in total", len(actuators))
        
        light_actuators = [
            actuator for actuator in actuators
            if any(state["factorId"] == FACTOR_BRIGHTNESS for state in actuator.get("states", []))
        ]
        
        _LOGGER.debug("Found %d light actuators: %s", 
                    len(light_actuators), 
                    [f"{a.get('id')} - {a.get('name')}" for a in light_actuators])
        
        return light_actuators

    async def get_cover_actuators(self) -> List[Dict[str, Any]]:
        """Get all cover actuators."""
        actuators = await self.get_actuators()
        return [
            actuator for actuator in actuators
            if any(state["factorId"] == FACTOR_BRIGHTNESS_EXT for state in actuator.get("states", []))
        ]

    async def get_climate_actuators(self) -> List[Dict[str, Any]]:
        """Get all climate actuators."""
        actuators = await self.get_actuators()
        return [
            actuator for actuator in actuators
            if any(state["factorId"] == FACTOR_TEMPERATURE for state in actuator.get("states", []))
        ]

    async def set_light_state(self, actuator_id: str, state: bool, brightness: Optional[int] = None) -> bool:
        """Set light state and brightness."""
        # True = 100, False = 0
        brightness_value = 100 if state and brightness is None else (brightness if brightness is not None else 0)
        
        data = {
            "value": brightness_value,
            "progressive": False,
        }
        
        result = await self._api_request(
            "PUT", 
            f"/intelligent-things/actuators/{actuator_id}/states/{FACTOR_BRIGHTNESS}",
            data
        )
        
        return isinstance(result, dict)

    async def set_cover_position(self, actuator_id: str, position: int) -> bool:
        """Set cover position (0-100)."""
        data = {
            "value": position,
            "progressive": True,
        }
        
        result = await self._api_request(
            "PUT", 
            f"/intelligent-things/actuators/{actuator_id}/states/{FACTOR_BRIGHTNESS_EXT}",
            data
        )
        
        return isinstance(result, dict)

    async def set_temperature(self, actuator_id: str, temperature: float) -> bool:
        """Set temperature."""
        data = {
            "value": temperature,
            "progressive": False,
        }
        
        result = await self._api_request(
            "PUT", 
            f"/intelligent-things/actuators/{actuator_id}/states/{FACTOR_TEMPERATURE}",
            data
        )
        
        return isinstance(result, dict)

    async def _api_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Make a request to the Hemis API."""
        url = f"{self.hemis_base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        _LOGGER.debug("API request: %s %s", method, url)
        if data:
            _LOGGER.debug("Request data: %s", data)
            
        try:
            async with async_timeout.timeout(10):
                if method == "GET":
                    response = await self.session.get(url, headers=headers)
                elif method == "PUT":
                    response = await self.session.put(url, headers=headers, json=data)
                elif method == "POST":
                    response = await self.session.post(url, headers=headers, json=data)
                else:
                    _LOGGER.error("Unsupported method: %s", method)
                    return None
                
                if response.status >= 400:
                    _LOGGER.error(
                        "Error from Hemis API: %s %s", 
                        response.status, 
                        await response.text()
                    )
                    return None
                
                if response.status == 204:  # No content
                    return {}
                
                result = await response.json()
                _LOGGER.debug("API response: %s", result)
                return result
                
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to Hemis API: %s", err)
            return None
        except async_timeout.TimeoutError:
            _LOGGER.error("Timeout connecting to Hemis API")
            return None
