"""Support for Flexom sensors."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    DOMAIN,
    FACTOR_BRIGHTNESS,
    FACTOR_BRIGHTNESS_EXT,
    FACTOR_TEMPERATURE,
    WS_TYPE_FACTOR_TARGET_STATE,
    WS_TYPE_FACTOR_CURRENT_STATE
)
from .hemis import HemisApiClient

_LOGGER = logging.getLogger(__name__)

FACTOR_UNITS = {
    FACTOR_BRIGHTNESS: "%",
    FACTOR_BRIGHTNESS_EXT: "%",
    FACTOR_TEMPERATURE: "°C",
}

FACTOR_NAMES = {
    FACTOR_BRIGHTNESS: "Brightness",
    FACTOR_BRIGHTNESS_EXT: "Roller Shutter",
    FACTOR_TEMPERATURE: "Temperature",
}

FACTOR_DEVICE_CLASSES = {
    FACTOR_BRIGHTNESS: None,
    FACTOR_BRIGHTNESS_EXT: None,
    FACTOR_TEMPERATURE: SensorDeviceClass.TEMPERATURE,
}

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Flexom Sensor from a config entry."""
    try:
        _LOGGER.info("Starting setup of Flexom Factor Sensors")
        hemis_client = hass.data[DOMAIN][config_entry.entry_id]["hemis_client"]
        coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
        
        # Get all zones to create sensors for factors
        _LOGGER.debug("Fetching zones from Hemis API")
        zones = await hemis_client.get_zones()
        _LOGGER.debug("Found %d zones: %s", len(zones), [f"{z.get('id')} - {z.get('name')}" for z in zones])
        
        entities = []
        
        # Create a sensor for each zone and factor combination
        for zone in zones:
            zone_id = zone.get("id")
            zone_name = zone.get("name", "Unknown Zone")
            
            if not zone_id:
                _LOGGER.warning("Skipping zone without ID: %s", zone)
                continue
                
            _LOGGER.debug("Creating sensors for zone: %s - %s", zone_id, zone_name)
            
            try:
                # Get factors for this zone
                _LOGGER.debug("Fetching factors for zone %s", zone_id)
                zone_factors = await hemis_client.get_zone_factors(zone_id)
                _LOGGER.debug("Found %d factors for zone %s: %s", 
                          len(zone_factors), 
                          zone_id, 
                          [f"{f.get('id')}" for f in zone_factors])
                
                for factor in zone_factors:
                    factor_id = factor.get("id")
                    if not factor_id:
                        _LOGGER.warning("Skipping factor without ID: %s", factor)
                        continue
                        
                    if factor_id in [FACTOR_BRIGHTNESS, FACTOR_BRIGHTNESS_EXT, FACTOR_TEMPERATURE]:
                        _LOGGER.debug("Creating sensor for factor %s in zone %s", factor_id, zone_id)
                        entities.append(
                            FlexomFactorSensor(
                                hemis_client,
                                coordinator,
                                zone,
                                factor_id
                            )
                        )
            except Exception as zone_err:
                _LOGGER.error("Error processing zone %s: %s", zone_id, zone_err, exc_info=True)
        
        _LOGGER.debug("Adding %d factor sensors", len(entities))
        if entities:
            async_add_entities(entities)
        else:
            _LOGGER.warning("No entities found to add")
    except Exception as err:
        _LOGGER.error("Failed to set up Flexom sensors: %s", err, exc_info=True)


class FlexomFactorSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Flexom Factor Sensor."""

    def __init__(
        self,
        hemis_client: HemisApiClient,
        coordinator: DataUpdateCoordinator,
        zone: Dict[str, Any],
        factor_id: str,
    ) -> None:
        """Initialize the factor sensor."""
        super().__init__(coordinator)
        self.hemis_client = hemis_client
        self.zone = zone
        self.factor_id = factor_id
        
        self._zone_id = zone.get("id", "")
        self._zone_name = zone.get("name", "Unknown Zone")
        self._state = None
        
        # Set the unique ID
        self._attr_unique_id = f"{DOMAIN}_factor_{self._zone_id}_{factor_id}"
        self._attr_name = f"{self._zone_name} {FACTOR_NAMES.get(factor_id, factor_id)}"
        
        # Add device class and unit
        self._attr_device_class = FACTOR_DEVICE_CLASSES.get(factor_id)
        self._attr_native_unit_of_measurement = FACTOR_UNITS.get(factor_id)
        
        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"zone_{self._zone_id}")},
            name=self._zone_name,
            manufacturer="Ubiant",
            model="Flexom Zone",
        )

    @property
    def native_value(self) -> Optional[float]:
        """Return the state of the sensor."""
        return self._state

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if not self.coordinator.data:
            return
            
        # Find factor state updates from WebSocket data
        for ws_data in self.coordinator.data:
            # Check for FACTOR_TARGET_STATE or FACTOR_CURRENT_STATE type messages
            if (
                ws_data.get("type") in [WS_TYPE_FACTOR_TARGET_STATE, WS_TYPE_FACTOR_CURRENT_STATE]
                and ws_data.get("factorId") == self.factor_id
                and ws_data.get("zoneId") == self._zone_id
            ):
                value = ws_data.get("value")
                if value is not None:
                    self._state = float(value)
                    self.async_write_ha_state()
                    _LOGGER.debug(
                        "Updated factor %s in zone %s: value=%s",
                        self.factor_id,
                        self._zone_id,
                        self._state
                    )
                    break
        
        super()._handle_coordinator_update()
