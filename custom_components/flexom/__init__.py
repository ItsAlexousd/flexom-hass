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

    # Create Hemis API client
    hemis_client = HemisApiClient(
        session,
        hemis_base_url,
        hemisphere_client.hemisphere_token
    )

    # Create WebSocket data queue for realtime updates
    ws_data_queue: List[Dict[str, Any]] = []

    # Create the WebSocket message handler
    @callback
    def handle_ws_message(message: Dict[str, Any]) -> None:
        """Handle messages from the WebSocket."""
        ws_data_queue.append(message)
        coordinator.async_set_updated_data(ws_data_queue.copy())
        # Keep only the last 50 messages
        while len(ws_data_queue) > 50:
            ws_data_queue.pop(0)

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
        raise ConfigEntryNotReady("Failed to connect to WebSocket")

    # Create update coordinator
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{building_id}",
        update_method=lambda: None,  # We don't poll, we get updates from WebSocket
    )

    # Start listening for WebSocket messages
    await ws_client.start_listening()

    # Store everything in hass.data for later use
    hass.data[DOMAIN][entry.entry_id] = {
        "hemisphere_client": hemisphere_client,
        "hemis_client": hemis_client,
        "ws_client": ws_client,
        "coordinator": coordinator,
    }

    # Set up all platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

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
