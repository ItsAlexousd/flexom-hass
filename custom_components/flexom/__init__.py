"""The Flexom integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
)
from .hemisphere import HemisphereApiClient
from .hemis import HemisApiClient
from .websocket import HemisWebSocketClient
from .debug_api import test_api_connectivity

_LOGGER = logging.getLogger(__name__)

# List the platforms that we want to support
# We'll start with just lights, and add cover and climate later
PLATFORMS = [Platform.LIGHT, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Flexom from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Get credentials from the config flow
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]

    # Run API diagnostics
    _LOGGER.info("Running API diagnostics")
    diagnostic_results = await test_api_connectivity(username, password)
    
    # Log diagnostic results
    if diagnostic_results["errors"]:
        _LOGGER.warning("API diagnostic found %d issues", len(diagnostic_results["errors"]))
        for error in diagnostic_results["errors"]:
            _LOGGER.warning("Diagnostic error: %s", error)
    else:
        _LOGGER.info("API diagnostic completed successfully with no errors")
        
    if diagnostic_results["zones"] is not None:
        _LOGGER.info("Found %d zones during diagnostic", diagnostic_results["zones"])
    
    if diagnostic_results["actuators"] is not None:
        _LOGGER.info("Found %d actuators during diagnostic", diagnostic_results["actuators"])

    # Create API clients
    session = async_get_clientsession(hass)
    hemisphere_client = HemisphereApiClient(session)

    # Authenticate with Hemisphere
    if not await hemisphere_client.authenticate(username, password):
        raise ConfigEntryNotReady("Failed to authenticate with Hemisphere")

    # Get Hemis building info
    building_id = hemisphere_client.building_id
    hemis_base_url = hemisphere_client.hemis_base_url
    hemis_stomp_url = hemisphere_client.hemis_stomp_url

    if not building_id or not hemis_base_url or not hemis_stomp_url:
        raise ConfigEntryNotReady("Failed to get Hemis building info")
        
    _LOGGER.info("Successfully authenticated with building ID: %s", building_id)
    _LOGGER.info("Hemis base URL: %s", hemis_base_url)
    _LOGGER.info("Hemis STOMP URL: %s", hemis_stomp_url)

    # Create Hemis API client
    hemis_client = HemisApiClient(
        session,
        hemis_base_url,
        hemisphere_client.hemisphere_token
    )
    
    # Test API connectivity - but don't fail if it doesn't work initially
    try:
        zones = await hemis_client.get_zones()
        if zones is None:
            _LOGGER.warning("Failed to fetch zones from Hemis API, but continuing setup")
        else:
            _LOGGER.info("Successfully fetched %d zones from Hemis API", len(zones))
    except Exception as api_err:
        _LOGGER.warning("Error testing Hemis API connectivity: %s - continuing setup", api_err)

    # Create WebSocket data queue for realtime updates
    ws_data_queue: List[Dict[str, Any]] = []

    # Create the WebSocket message handler
    @callback
    def handle_ws_message(message: Dict[str, Any]) -> None:
        """Handle messages from the WebSocket."""
        try:
            # Add message to the queue
            ws_data_queue.append(message)
            
            # Log message for debugging
            msg_type = message.get("type", "unknown")
            msg_id = message.get("id", "unknown")
            
            # Get actuator or zone ID if present
            entity_id = (
                message.get("actuatorId") or 
                message.get("itId") or 
                message.get("zoneId") or 
                "unknown"
            )
            
            # Get factor ID if present
            factor_id = message.get("factorId", "unknown")
            
            # Log a summary of the message
            _LOGGER.debug(
                "WebSocket message: type=%s, entity_id=%s, factor=%s",
                msg_type,
                entity_id,
                factor_id
            )
            
            # Update coordinator data
            coordinator.async_set_updated_data(ws_data_queue.copy())
            
            # Keep only the last 50 messages
            while len(ws_data_queue) > 50:
                ws_data_queue.pop(0)
                
        except Exception as err:
            _LOGGER.error("Error processing WebSocket message: %s", err, exc_info=True)

    # Create WebSocket client
    ws_client = HemisWebSocketClient(
        hass,
        hemis_stomp_url,
        building_id,
        hemisphere_client.hemisphere_token,
        handle_ws_message
    )

    # Connect to WebSocket
    if not await ws_client.connect():
        _LOGGER.warning(
            "Failed to connect to WebSocket initially. Integration will continue "
            "to setup but may not receive real-time updates. "
            "This will be retried automatically in the background."
        )
        # Start a background task to retry connection
        hass.async_create_task(ws_client.reconnect())
    else:
        # Start listening for WebSocket messages
        await ws_client.start_listening()

    # Create update coordinator
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{building_id}",
        update_method=lambda: None,  # We don't poll, we get updates from WebSocket
    )

    # Store everything in hass.data for later use
    hass.data[DOMAIN][entry.entry_id] = {
        "hemisphere_client": hemisphere_client,
        "hemis_client": hemis_client,
        "ws_client": ws_client,
        "coordinator": coordinator,
    }

    # Set up all platforms
    try:
        _LOGGER.info("Setting up platforms: %s", PLATFORMS)
        
        # Log more detailed info about what we're passing to the platforms
        _LOGGER.debug("Hemis base URL for platform setup: %s", hemis_base_url)
        _LOGGER.debug("Building ID for platform setup: %s", building_id)
        _LOGGER.debug("WebSocket URL for platform setup: %s", hemis_stomp_url)
        
        # Try to get actuators to verify API access
        actuators = await hemis_client.get_actuators()
        if actuators is None:
            _LOGGER.error("Could not get actuators from API - API access may be failing")
        else:
            _LOGGER.info("API access verified - found %d actuators", len(actuators))
            # List actual actuator info
            for i, actuator in enumerate(actuators[:5]):  # Show first 5 only to avoid log spam
                _LOGGER.info("Actuator %d/%d: id=%s, name=%s, type=%s", 
                             i+1, len(actuators),
                             actuator.get("id"), 
                             actuator.get("name"),
                             actuator.get("typeName"))
                
                # Show actuator states
                states = actuator.get("states", [])
                if states:
                    _LOGGER.info("  States for %s: %s", 
                                 actuator.get("name"),
                                 ", ".join(f"{s.get('factorId')}={s.get('value')}" for s in states[:3]))
        
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        # Log success
        _LOGGER.info("Successfully set up platforms")
    except Exception as err:
        _LOGGER.error("Error setting up platforms: %s", err, exc_info=True)
        # Log additional context
        _LOGGER.error("Entry data: %s", entry.data)
        _LOGGER.error("Building ID: %s", building_id)
        raise

    # Define update listener to reload entry when options change
    entry.async_on_unload(entry.add_update_listener(update_listener))

    # Setup is successful
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Disconnect WebSocket
        ws_client = hass.data[DOMAIN][entry.entry_id]["ws_client"]
        await ws_client.disconnect()
        
        # Remove data
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
