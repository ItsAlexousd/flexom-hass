"""Debug utility for Flexom API."""
import asyncio
import aiohttp
import logging
import json
from typing import Any, Dict, List, Optional

from . import hemisphere
from . import hemis
from .const import (
    HEMISPHERE_URL,
    HEMISPHERE_SIGNIN_URL,
    HEMISPHERE_BUILDINGS_URL,
    HEMIS_BASE_URL_TEMPLATE,
    FACTOR_BRIGHTNESS,
    FACTOR_BRIGHTNESS_EXT,
    FACTOR_TEMPERATURE,
)

_LOGGER = logging.getLogger(__name__)

async def test_api_connectivity(username: str, password: str) -> None:
    """Test connectivity to all APIs and print results."""
    try:
        _LOGGER.info("=== Starting Flexom API diagnostic ===")
        
        # Create session
        session = aiohttp.ClientSession()
        
        try:
            # Test Hemisphere API
            _LOGGER.info("Testing Hemisphere API...")
            hemisphere_client = hemisphere.HemisphereApiClient(session)
            
            success = await hemisphere_client.authenticate(username, password)
            _LOGGER.info("Authentication result: %s", success)
            
            if success:
                _LOGGER.info("Hemisphere token: %s", hemisphere_client.hemisphere_token[:10] + "...")
                _LOGGER.info("Building ID: %s", hemisphere_client.building_id)
                _LOGGER.info("Hemis base URL: %s", hemisphere_client.hemis_base_url)
                _LOGGER.info("Hemis STOMP URL: %s", hemisphere_client.hemis_stomp_url)
                
                # Test Hemis API
                _LOGGER.info("Testing Hemis API...")
                hemis_client = hemis.HemisApiClient(
                    session,
                    hemisphere_client.hemis_base_url,
                    hemisphere_client.hemisphere_token
                )
                
                # Get zones
                _LOGGER.info("Fetching zones...")
                zones = await hemis_client.get_zones()
                if zones is None:
                    _LOGGER.error("Failed to fetch zones")
                else:
                    _LOGGER.info("Found %d zones", len(zones))
                    for zone in zones:
                        _LOGGER.info("Zone: %s - %s", zone.get("id"), zone.get("name"))
                        
                        # Get factors for zone
                        zone_id = zone.get("id")
                        if zone_id:
                            _LOGGER.info("Fetching factors for zone %s...", zone_id)
                            factors = await hemis_client.get_zone_factors(zone_id)
                            if factors is None:
                                _LOGGER.error("Failed to fetch factors for zone %s", zone_id)
                            else:
                                _LOGGER.info("Found %d factors for zone %s", len(factors), zone_id)
                                for factor in factors:
                                    _LOGGER.info("Factor: %s", factor.get("id"))
                
                # Get actuators
                _LOGGER.info("Fetching actuators...")
                actuators = await hemis_client.get_actuators()
                if actuators is None:
                    _LOGGER.error("Failed to fetch actuators")
                else:
                    _LOGGER.info("Found %d actuators", len(actuators))
                    for actuator in actuators:
                        _LOGGER.info("Actuator: %s - %s (zoneId: %s)", 
                                     actuator.get("id"), 
                                     actuator.get("name"),
                                     actuator.get("zoneId"))
                        
                        # Check states
                        states = actuator.get("states", [])
                        _LOGGER.info("Actuator has %d states", len(states))
                        for state in states:
                            _LOGGER.info("State: %s", state.get("factorId"))
                
                # Get light actuators
                _LOGGER.info("Fetching light actuators...")
                light_actuators = await hemis_client.get_light_actuators()
                if light_actuators is None:
                    _LOGGER.error("Failed to fetch light actuators")
                else:
                    _LOGGER.info("Found %d light actuators", len(light_actuators))
                    for actuator in light_actuators:
                        _LOGGER.info("Light actuator: %s - %s", 
                                     actuator.get("id"), 
                                     actuator.get("name"))
            
        finally:
            await session.close()
            
        _LOGGER.info("=== Flexom API diagnostic complete ===")
    except Exception as err:
        _LOGGER.error("Error in API diagnostic: %s", err, exc_info=True)
