"""Sensor platform for CHJ SAIH integration."""
from __future__ import annotations

from datetime import datetime, timedelta # Added datetime
import logging # Ensure logging is imported if LOGGER from .const isn't used directly for all logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback # Added callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
# async_get_clientsession and aiohttp might not be needed if all fetching is in coordinator
# import aiohttp # For ClientError
# from homeassistant.helpers.aiohttp_client import async_get_clientsession

# from chj_saih import fetch_sensor_data # No longer directly used by sensor
from homeassistant.helpers.update_coordinator import CoordinatorEntity # Added

from .coordinator import ChjSaihDataUpdateCoordinator # Added

from .const import (
    DOMAIN,
    CONF_STATIONS,
    LOGGER, # Using the logger from const.py
    ATTR_LAST_UPDATE,
    ATTR_DATA_URL,
    ATTR_RIVER_NAME,
    ATTR_STATION_NAME,
    ATTR_STATION_ID,
)

# SCAN_INTERVAL is typically managed by the DataUpdateCoordinator if one is used.
# If not, individual entities might manage their own scan interval or rely on a global one.
# For now, let's assume updates are driven by HA's default or a coordinator.
# SCAN_INTERVAL = timedelta(minutes=15) # Example, if not using coordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the CHJ SAIH sensor platform."""
    station_ids: list[str] = entry.data[CONF_STATIONS]
    # config_scan_interval = entry.options.get(CONF_SCAN_INTERVAL) # Or from entry.data

    LOGGER.info("Setting up CHJ SAIH sensors for stations: %s", station_ids)

    sensors_to_add: list[ChjSaihSpecificSensor] = []

    # Placeholder: Determine what kind of sensors each station_id provides.
    # This will likely involve either:
    # 1. Predefined sensor types per station if known.
    # 2. Fetching metadata for each station to discover its available sensors (e.g., flow, level).
    # For now, we'll create one generic sensor per station_id as a placeholder.
    coordinator: ChjSaihDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    station_ids: list[str] = entry.data[CONF_STATIONS] # Or coordinator.station_ids

    sensors_to_add: list[ChjSaihSensor] = []
    for station_id in station_ids:
        # Create one sensor entity per station_id (variable)
        sensors_to_add.append(ChjSaihSensor(coordinator, station_id))

    if sensors_to_add:
        LOGGER.info("Adding %d CHJ SAIH sensors to Home Assistant", len(sensors_to_add))
        async_add_entities(sensors_to_add) # update_before_add is not strictly needed with coordinator
    else:
        LOGGER.info("No CHJ SAIH sensors to add for entry %s.", entry.entry_id)


class ChjSaihSensor(CoordinatorEntity[ChjSaihDataUpdateCoordinator], SensorEntity):
    """Representation of a sensor from a CHJ SAIH station (variable), managed by a coordinator."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ChjSaihDataUpdateCoordinator,
        station_id: str, # This is the 'variable' ID
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._station_id = station_id
        self._config_entry_id = coordinator.config_entry.entry_id # For unique ID

        self._attr_unique_id = f"{self._config_entry_id}_{self._station_id}"

        # Initialize attributes that will be updated by _handle_coordinator_update
        self._attr_name = None # Will be set by the first update
        self._attr_native_value = None
        self._attr_native_unit_of_measurement = None
        self._attr_extra_state_attributes = {ATTR_STATION_ID: self._station_id}

        # Initial Device Info - can be refined in _handle_coordinator_update
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._station_id)}, # Using variable_id as device for now
            "name": f"CHJ SAIH {self._station_id}", # Placeholder
            "manufacturer": "CHJ Confederación Hidrográfica del Júcar",
            "model": "SAIH Monitoring Point",
            "entry_type": "service",
            "via_device": (DOMAIN, self._config_entry_id) # Link to config entry device if one exists
        }
        # Call initial update to set initial state from potentially already fetched data
        self._update_attrs_from_coordinator_data()
        LOGGER.debug("Initialized sensor %s for station_id (variable): %s", self.unique_id, self._station_id)


    @property
    def _sensor_data(self) -> dict | None:
        """Return the specific data for this sensor from coordinator."""
        if self.coordinator.data:
            return self.coordinator.data.get(self._station_id)
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Available if coordinator is available and this specific sensor has data without error
        return (
            super().available # Checks coordinator.last_update_success
            and self._sensor_data is not None
            and not self._sensor_data.get("error")
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        LOGGER.debug("Handling coordinator update for sensor %s", self._station_id)
        self._update_attrs_from_coordinator_data()
        self.async_write_ha_state()

    def _update_attrs_from_coordinator_data(self) -> None:
        """Update entity attributes from coordinator data."""
        if self._sensor_data and not self._sensor_data.get("error"):
            self._attr_name = self._sensor_data.get("name", f"CHJ SAIH {self._station_id}")
            self._attr_native_value = self._sensor_data.get("value")
            self._attr_native_unit_of_measurement = self._sensor_data.get("unit")

            new_extra_attrs = {ATTR_STATION_ID: self._station_id}
            if self._sensor_data.get(ATTR_LAST_UPDATE):
                new_extra_attrs[ATTR_LAST_UPDATE] = self._sensor_data[ATTR_LAST_UPDATE]

            metadata = self._sensor_data.get("metadata", {})
            if metadata:
                # Use more specific station name for the device if available
                station_name_from_meta = metadata.get('nombreEstacion', self._attr_name)
                # Fallback to variable description if nombreEstacion is generic or missing
                if not station_name_from_meta or station_name_from_meta == self._attr_name :
                     station_name_from_meta = metadata.get('descripcion', self._attr_name)

                self._attr_device_info["name"] = station_name_from_meta

                station_code = metadata.get('codigoEstacion')
                if station_code:
                    self._attr_device_info["model"] = f"Station Code: {station_code}"
                    # Consider if codigoEstacion should be the device identifier
                    # self._attr_device_info["identifiers"] = {(DOMAIN, station_code)}

                new_extra_attrs[ATTR_STATION_NAME] = metadata.get('nombreEstacion')
                new_extra_attrs[ATTR_RIVER_NAME] = metadata.get('nombreRio')
                # Example: self._attr_extra_state_attributes[ATTR_DATA_URL] = ...

            self._attr_extra_state_attributes = new_extra_attrs

            # Log if name or unit is unexpectedly None after update
            if self._attr_name is None:
                LOGGER.debug("Sensor name is None after update for %s", self._station_id)
            if self._attr_native_unit_of_measurement is None:
                 LOGGER.debug("Sensor unit is None after update for %s", self._station_id)

        elif self._sensor_data and self._sensor_data.get("error"):
            LOGGER.warning(
                "Sensor %s has error in coordinator data: %s - %s",
                self.entity_id if self.entity_id else self._station_id, # self.entity_id might be None during init
                self._sensor_data.get("error"),
                self._sensor_data.get("details", "")
            )
            # Decide how to handle entity state on error, e.g., clear value, keep old, etc.
            # For now, native_value will be None if not set by successful update.
            # If the error is 'no_readings' or 'value_parse_error', metadata might still be useful
            metadata = self._sensor_data.get("metadata", {})
            if metadata:
                self._attr_name = self._sensor_data.get("name", metadata.get('descripcion', f"CHJ SAIH {self._station_id}"))
                self._attr_native_unit_of_measurement = self._sensor_data.get("unit", metadata.get('dimension') or metadata.get('tipoVariable', {}).get('unidades'))
                station_name_from_meta = metadata.get('nombreEstacion', self._attr_name)
                if not station_name_from_meta or station_name_from_meta == self._attr_name :
                     station_name_from_meta = metadata.get('descripcion', self._attr_name)
                self._attr_device_info["name"] = station_name_from_meta
                station_code = metadata.get('codigoEstacion')
                if station_code:
                    self._attr_device_info["model"] = f"Station Code: {station_code}"


    # Properties like native_value, name, unit_of_measurement, extra_state_attributes
    # will now use the _attr_ versions set by _handle_coordinator_update or _update_attrs_from_coordinator_data.
    # No need to override them if _attr_ versions are correctly managed.
