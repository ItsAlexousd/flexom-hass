"""Hemis API client."""
import logging
from typing import Any, Dict, List, Optional

import aiohttp
import asyncio

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
        return await self._api_call("/zones")

    async def get_zone_factors(self, zone_id: str) -> List[Dict[str, Any]]:
        """Get all factors for a zone."""
        return await self._api_call(f"/zones/{zone_id}/factors")

    async def get_sensors(self) -> List[Dict[str, Any]]:
        """Get all sensors."""
        return await self._api_call("/intelligent-things/sensors")

    async def get_actuators(self) -> List[Dict[str, Any]]:
        """Get all actuators."""
        return await self._api_call("/intelligent-things/actuators")

    async def get_light_actuators(self) -> List[Dict[str, Any]]:
        """Get all light actuators."""
        _LOGGER.debug("Fetching light actuators")
        actuators = await self.get_actuators()
        
        if actuators is None:
            _LOGGER.error("Failed to get actuators, returning empty list")
            return []
            
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
        
        result = await self._api_call(
            f"/intelligent-things/actuators/{actuator_id}/states/{FACTOR_BRIGHTNESS}",
            method="PUT",
            data=data
        )
        
        return isinstance(result, dict)

    async def set_cover_position(self, actuator_id: str, position: int) -> bool:
        """Set cover position (0-100)."""
        data = {
            "value": position,
            "progressive": True,
        }
        
        result = await self._api_call(
            f"/intelligent-things/actuators/{actuator_id}/states/{FACTOR_BRIGHTNESS_EXT}",
            method="PUT",
            data=data
        )
        
        return isinstance(result, dict)

    async def set_temperature(self, actuator_id: str, temperature: float) -> bool:
        """Set temperature."""
        data = {
            "value": temperature,
            "progressive": False,
        }
        
        result = await self._api_call(
            f"/intelligent-things/actuators/{actuator_id}/states/{FACTOR_TEMPERATURE}",
            method="PUT",
            data=data
        )
        
        return isinstance(result, dict)

    async def _api_call(self, endpoint, method="GET", data=None, headers=None):
        """Make an API call to the Hemis API."""
        url = f"{self.hemis_base_url}{endpoint}"
        _LOGGER.debug("API call: %s %s", method, url)
        
        headers = headers or {}
        headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        })
        
        # Print the first 10 characters of the token for debugging
        _LOGGER.debug("Using token for API call: %s...", self.token[:10] if self.token else "None")

        # Add longer timeout for potentially slow servers
        timeout = 30

        for retry in range(5):  # Increase retries to 5
            try:
                if method == "GET":
                    _LOGGER.debug("Sending GET request to %s (attempt %s/5)", url, retry + 1)
                    async with self.session.get(
                        url, headers=headers, timeout=timeout
                    ) as response:
                        if response.status != 200:
                            _LOGGER.error(
                                "Error calling %s: %s %s",
                                url,
                                response.status,
                                response.reason,
                            )
                            # Handle 401 Unauthorized - could be token expiration
                            if response.status == 401 and retry < 4:
                                wait_time = (retry + 1) * 2
                                _LOGGER.warning(
                                    "Received 401 Unauthorized, retrying in %s seconds (attempt %s/5)",
                                    wait_time,
                                    retry + 1
                                )
                                # Could add token refresh logic here
                                await asyncio.sleep(wait_time)
                                continue
                            # If we got a 502, retry after a delay with longer timeout
                            if response.status == 502 and retry < 4:
                                wait_time = (retry + 1) * 5  # Increase wait time
                                timeout += 10  # Increase timeout each retry
                                _LOGGER.warning(
                                    "Received 502 Bad Gateway, retrying in %s seconds with timeout=%s (attempt %s/5)",
                                    wait_time,
                                    timeout,
                                    retry + 1
                                )
                                await asyncio.sleep(wait_time)
                                continue
                            return None
                        
                        # Log success
                        _LOGGER.debug("Successful response from %s", url)
                        
                        # Parse JSON response
                        try:
                            data = await response.json()
                            _LOGGER.debug("Parsed JSON response from %s: %d items", url, len(data) if isinstance(data, list) else 1)
                            return data
                        except Exception as err:
                            _LOGGER.error("Error parsing JSON from %s: %s", url, err)
                            return None
                elif method == "POST":
                    _LOGGER.debug("Sending POST request to %s (attempt %s/5)", url, retry + 1)
                    async with self.session.post(
                        url, headers=headers, json=data, timeout=timeout
                    ) as response:
                        if response.status != 200:
                            _LOGGER.error(
                                "Error calling %s: %s %s",
                                url,
                                response.status,
                                response.reason,
                            )
                            # Handle 401 Unauthorized - could be token expiration
                            if response.status == 401 and retry < 4:
                                wait_time = (retry + 1) * 2
                                _LOGGER.warning(
                                    "Received 401 Unauthorized, retrying in %s seconds (attempt %s/5)",
                                    wait_time,
                                    retry + 1
                                )
                                # Could add token refresh logic here
                                await asyncio.sleep(wait_time)
                                continue
                            # If we got a 502, retry after a delay with longer timeout
                            if response.status == 502 and retry < 4:
                                wait_time = (retry + 1) * 5  # Increase wait time
                                timeout += 10  # Increase timeout each retry
                                _LOGGER.warning(
                                    "Received 502 Bad Gateway, retrying in %s seconds with timeout=%s (attempt %s/5)",
                                    wait_time,
                                    timeout,
                                    retry + 1
                                )
                                await asyncio.sleep(wait_time)
                                continue
                            return None
                        
                        # Log success
                        _LOGGER.debug("Successful POST response from %s", url)
                        
                        # Parse JSON response
                        try:
                            data = await response.json()
                            _LOGGER.debug("Parsed JSON response from POST to %s", url)
                            return data
                        except Exception as err:
                            _LOGGER.error("Error parsing JSON from POST to %s: %s", url, err)
                            return None
                elif method == "PUT":
                    _LOGGER.debug("Sending PUT request to %s (attempt %s/5)", url, retry + 1)
                    async with self.session.put(
                        url, headers=headers, json=data, timeout=timeout
                    ) as response:
                        if response.status != 200:
                            _LOGGER.error(
                                "Error calling %s: %s %s",
                                url,
                                response.status,
                                response.reason,
                            )
                            # Handle 401 Unauthorized - could be token expiration
                            if response.status == 401 and retry < 4:
                                wait_time = (retry + 1) * 2
                                _LOGGER.warning(
                                    "Received 401 Unauthorized, retrying in %s seconds (attempt %s/5)",
                                    wait_time,
                                    retry + 1
                                )
                                # Could add token refresh logic here
                                await asyncio.sleep(wait_time)
                                continue
                            # If we got a 502, retry after a delay with longer timeout
                            if response.status == 502 and retry < 4:
                                wait_time = (retry + 1) * 5  # Increase wait time
                                timeout += 10  # Increase timeout each retry
                                _LOGGER.warning(
                                    "Received 502 Bad Gateway, retrying in %s seconds with timeout=%s (attempt %s/5)",
                                    wait_time,
                                    timeout,
                                    retry + 1
                                )
                                await asyncio.sleep(wait_time)
                                continue
                            return None
                        
                        # Log success
                        _LOGGER.debug("Successful PUT response from %s", url)
                        
                        # Parse JSON response if available
                        if response.status == 204:  # No content
                            _LOGGER.debug("No content in PUT response (status 204)")
                            return {}
                            
                        try:
                            data = await response.json()
                            _LOGGER.debug("Parsed JSON response from PUT to %s", url)
                            return data
                        except Exception as err:
                            _LOGGER.error("Error parsing JSON from PUT to %s: %s", url, err)
                            return None
            except asyncio.TimeoutError:
                _LOGGER.error("Timeout calling %s (attempt %s/5)", url, retry + 1)
                if retry < 4:
                    wait_time = (retry + 1) * 5
                    timeout += 10  # Increase timeout each retry
                    _LOGGER.warning("Increasing timeout to %s seconds for next attempt", timeout)
                    await asyncio.sleep(wait_time)
                    continue
                return None
            except (aiohttp.ClientError, asyncio.exceptions.CancelledError) as err:
                _LOGGER.error("Error calling %s: %s (attempt %s/5)", url, err, retry + 1)
                if retry < 4:
                    wait_time = (retry + 1) * 5
                    await asyncio.sleep(wait_time)
                    continue
                return None
        
        # If we got here, all retries failed
        return None
