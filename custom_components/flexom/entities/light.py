"""Support for Flexom lights."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from ..const import DOMAIN, FACTOR_BRIGHTNESS, WS_TYPE_ACTUATOR_HARDWARE_STATE, WS_TYPE_FACTOR_TARGET_STATE
from ..hemis import HemisApiClient

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Flexom Light from a config entry."""
    hemis_client = hass.data[DOMAIN][config_entry.entry_id]["hemis_client"]
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    
    # Get all light actuators
    _LOGGER.debug("Setting up Flexom Light entities")
    actuators = await hemis_client.get_light_actuators()
    _LOGGER.debug("Found %d light actuators", len(actuators))
    
    entities = []
    for actuator in actuators:
        _LOGGER.debug("Processing actuator: %s - %s (zoneId: %s)", 
                     actuator.get("id"), 
                     actuator.get("name"),
                     actuator.get("zoneId"))
        # Find the BRI state in the actuator states
        for state in actuator.get("states", []):
            if state.get("factorId") == FACTOR_BRIGHTNESS:
                _LOGGER.debug("Found BRI state for actuator %s: %s", 
                             actuator.get("id"), 
                             state)
                entities.append(
                    FlexomLight(
                        hemis_client,
                        coordinator,
                        actuator,
                        state
                    )
                )
                break
    
    _LOGGER.debug("Adding %d light entities", len(entities))
    async_add_entities(entities)


class FlexomLight(CoordinatorEntity, LightEntity):
    """Representation of a Flexom Light."""

    def __init__(
        self,
        hemis_client: HemisApiClient,
        coordinator: DataUpdateCoordinator,
        actuator: Dict[str, Any],
        state: Dict[str, Any],
    ) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        self.hemis_client = hemis_client
        self.actuator = actuator
        self.state_info = state
        
        self._id = actuator.get("id", "")
        self._name = actuator.get("name", "Unknown")
        self._state = False
        self._brightness = 0
        
        # Set the unique ID
        self._attr_unique_id = f"{DOMAIN}_light_{self._id}"
        self._attr_name = self._name
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        
        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._id)},
            name=self._name,
            manufacturer="Ubiant",
            model="Flexom Light",
        )

    @property
    def is_on(self) -> bool:
        """Return true if the light is on."""
        return self._state

    @property
    def brightness(self) -> Optional[int]:
        """Return the brightness of this light between 0..255."""
        # Convert 0-100 to 0-255
        return int(self._brightness * 255 / 100) if self._brightness is not None else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        
        # Convert brightness from 0-255 to 0-100
        if brightness is not None:
            brightness_pct = int(brightness * 100 / 255)
        else:
            brightness_pct = 100
            
        await self.hemis_client.set_light_state(self._id, True, brightness_pct)
        
        self._state = True
        self._brightness = brightness_pct
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        await self.hemis_client.set_light_state(self._id, False)
        
        self._state = False
        self._brightness = 0
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if not self.coordinator.data:
            return
            
        # Find actuator state updates from WebSocket data
        for ws_data in self.coordinator.data:
            # Check for ACTUATOR_HARDWARE_STATE type messages
            if (
                ws_data.get("type") == WS_TYPE_ACTUATOR_HARDWARE_STATE
                and ws_data.get("factorId") == FACTOR_BRIGHTNESS
            ):
                value_data = ws_data.get("value", {})
                actuator_id = value_data.get("actuatorId")
                
                if actuator_id and actuator_id.startswith(self._id):
                    value = value_data.get("value")
                    if value is not None:
                        self._brightness = float(value)
                        self._state = self._brightness > 0
                        self.async_write_ha_state()
                        break
            
            # Check for FACTOR_TARGET_STATE type messages - these come directly from the server
            elif (
                ws_data.get("type") == WS_TYPE_FACTOR_TARGET_STATE
                and ws_data.get("factorId") == FACTOR_BRIGHTNESS
                and ws_data.get("zoneId") == self.actuator.get("zoneId")
            ):
                value = ws_data.get("value")
                if value is not None:
                    self._brightness = float(value)
                    self._state = self._brightness > 0
                    self.async_write_ha_state()
                    _LOGGER.debug(
                        "Updated light %s from FACTOR_TARGET_STATE: brightness=%s, state=%s",
                        self._id,
                        self._brightness,
                        self._state
                    )
                    break
        
        super()._handle_coordinator_update()
