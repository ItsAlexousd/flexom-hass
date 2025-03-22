"""Support for Flexom lights."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, FACTOR_BRIGHTNESS, WS_TYPE_ACTUATOR_HARDWARE_STATE, WS_TYPE_FACTOR_TARGET_STATE
from .hemis import HemisApiClient

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Flexom Light from a config entry."""
    _LOGGER.debug("Setting up Flexom Light entities")
    
    data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = data["coordinator"]
    hemis_client = data["hemis_client"]
    
    try:
        # Fetch light actuators from Hemis API
        light_actuators = await hemis_client.get_light_actuators()
        if not light_actuators:
            _LOGGER.info("No light actuators found")
            return
            
        _LOGGER.info("Found %d light actuators", len(light_actuators))
        
        # Create entities
        entities = []
        for actuator in light_actuators:
            try:
                actuator_id = actuator.get("id")
                actuator_name = actuator.get("name")
                _LOGGER.debug("Creating light entity for: %s (%s)", actuator_name, actuator_id)
                
                # Verify that the actuator has the required states
                has_brightness = any(
                    state["factorId"] == FACTOR_BRIGHTNESS for state in actuator.get("states", [])
                )
                
                if not has_brightness:
                    _LOGGER.warning(
                        "Actuator %s (%s) doesn't have brightness factor, skipping",
                        actuator_name,
                        actuator_id
                    )
                    continue
                    
                # Create the entity
                entities.append(
                    FlexomLight(
                        coordinator=coordinator,
                        hemis_client=hemis_client,
                        actuator=actuator,
                    )
                )
            except Exception as err:
                _LOGGER.error(
                    "Error creating light entity for %s: %s",
                    actuator.get("name", actuator.get("id", "unknown")),
                    str(err),
                    exc_info=True
                )
        
        # Add entities to Home Assistant
        if entities:
            _LOGGER.info("Adding %d light entities", len(entities))
            async_add_entities(entities)
        else:
            _LOGGER.warning("No valid light entities were created")
    
    except Exception as err:
        _LOGGER.error("Error setting up Flexom Light entities: %s", str(err), exc_info=True)


class FlexomLight(CoordinatorEntity, LightEntity):
    """Representation of a Flexom light."""

    def __init__(
        self,
        hemis_client: HemisApiClient,
        coordinator: DataUpdateCoordinator,
        actuator: Dict[str, Any],
    ) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        self.hemis_client = hemis_client
        self.actuator = actuator
        
        self._id = actuator.get("id", "")
        self._name = actuator.get("name", "Unknown Light")
        self._zone_id = actuator.get("zoneId", "")
        self._type_name = actuator.get("typeName", "")
        self._is_on = False
        self._brightness = 0
        
        # Set color mode attributes
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        
        # Find initial state
        for state in actuator.get("states", []):
            if state.get("factorId") == FACTOR_BRIGHTNESS:
                self._brightness = int(state.get("value", 0))
                self._is_on = self._brightness > 0
                break
        
        _LOGGER.debug(
            "Initialized light %s with brightness %s (on: %s)",
            self._name,
            self._brightness,
            self._is_on
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{DOMAIN}_{self._id}"

    @property
    def name(self) -> str:
        """Return the name of the light."""
        return self._name

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._is_on

    @property
    def brightness(self) -> int:
        """Return the brightness of this light between 0..255."""
        return round(self._brightness * 255 / 100)

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return LightEntityFeature.BRIGHTNESS

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._id)},
            "name": self._name,
            "manufacturer": "Ubiant",
            "model": self._type_name or "Light Actuator",
            "via_device": (DOMAIN, self._zone_id) if self._zone_id else None,
        }

    @property
    def should_poll(self) -> bool:
        """No polling needed since we're using the coordinator."""
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS, None)
        if brightness is not None:
            # Convert from 0-255 to 0-100
            brightness_value = round(brightness * 100 / 255)
        else:
            brightness_value = 100 if not self._is_on else self._brightness
        
        _LOGGER.debug("Turning on light %s with brightness %s", self._name, brightness_value)
        
        success = await self.hemis_client.set_light_state(
            self._id, True, brightness_value
        )
        
        if success:
            self._is_on = True
            self._brightness = brightness_value
            self.async_write_ha_state()
        else:
            _LOGGER.error("Failed to turn on light %s", self._name)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        _LOGGER.debug("Turning off light %s", self._name)
        
        success = await self.hemis_client.set_light_state(self._id, False)
        
        if success:
            self._is_on = False
            self._brightness = 0
            self.async_write_ha_state()
        else:
            _LOGGER.error("Failed to turn off light %s", self._name)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if not self.coordinator.data:
            return
            
        try:
            # Parse WebSocket data and update device state
            for message in reversed(self.coordinator.data):
                # Check if this is a ACTUATOR_TARGET_STATE message for this device
                if (
                    message.get("type") == "ACTUATOR_TARGET_STATE"
                    and message.get("actuatorId") == self._id
                    and message.get("factorId") == FACTOR_BRIGHTNESS
                ):
                    value = message.get("value")
                    if value is not None:
                        self._brightness = float(value)
                        self._is_on = self._brightness > 0
                        self.async_write_ha_state()
                        _LOGGER.debug(
                            "Updated light %s from ACTUATOR_TARGET_STATE: brightness=%s, state=%s",
                            self._id,
                            self._brightness,
                            self._is_on
                        )
                        break
                
                # Also check for FACTOR_TARGET_STATE as an alternative
                if (
                    message.get("type") == "FACTOR_TARGET_STATE"
                    and message.get("itId") == self._id
                    and message.get("factorId") == FACTOR_BRIGHTNESS
                ):
                    value = message.get("value")
                    if value is not None:
                        self._brightness = float(value)
                        self._is_on = self._brightness > 0
                        self.async_write_ha_state()
                        _LOGGER.debug(
                            "Updated light %s from FACTOR_TARGET_STATE: brightness=%s, state=%s",
                            self._id,
                            self._brightness,
                            self._is_on
                        )
                        break
                        
                # Check for ACTUATOR_CURRENT_STATE for live updates
                if (
                    message.get("type") == "ACTUATOR_CURRENT_STATE"
                    and message.get("actuatorId") == self._id
                    and message.get("factorId") == FACTOR_BRIGHTNESS
                ):
                    value = message.get("value")
                    if value is not None:
                        self._brightness = float(value)
                        self._is_on = self._brightness > 0
                        self.async_write_ha_state()
                        _LOGGER.debug(
                            "Updated light %s from ACTUATOR_CURRENT_STATE: brightness=%s, state=%s",
                            self._id,
                            self._brightness,
                            self._is_on
                        )
                        break
        except Exception as err:
            _LOGGER.error(
                "Error handling coordinator update for light %s: %s",
                self._name,
                str(err),
                exc_info=True
            )
