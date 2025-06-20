from datetime import timedelta
import logging # Retained for context, but LOGGER from .const will be used

from chj_saih import APIClient  # Assuming direct import
from chj_saih.exceptions import SaihError # Assuming base error

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.const import CONF_SCAN_INTERVAL

from .const import (
    DOMAIN,
    LOGGER, # Use this logger
    CONF_STATIONS,
    ATTR_LAST_UPDATE, # For station data attribute
    ATTR_RIVER_NAME,  # Example attribute
    ATTR_STATION_NAME, # For entity name / device name
    # ATTR_STATION_ID is also in const.py, can be used if needed for attributes
)

# SCAN_INTERVAL is handled by the coordinator's update_interval

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up CHJ SAIH sensor entities based on a config entry."""

    entry_data = hass.data[DOMAIN][entry.entry_id]
    station_ids = entry_data.get(CONF_STATIONS, []) # Use .get for safety
    scan_interval_seconds = entry_data[CONF_SCAN_INTERVAL]

    if not station_ids:
        LOGGER.warning("No station IDs configured for CHJ SAIH for entry %s.", entry.entry_id)
        return

    # It's good practice to create one API client instance per config entry (or per HASS instance)
    # if the client is lightweight or connectionless. If it manages a connection pool or session,
    # this approach is fine.
    api_client = APIClient()

    sensors = []
    for station_id in station_ids:
        coordinator = ChjSaihStationCoordinator(
            hass,
            api_client,
            station_id,
            timedelta(seconds=scan_interval_seconds),
        )
        # Fetch initial data so entities are created with actual data if possible
        # This also helps in setting up device_info and entity name correctly if derived from data
        await coordinator.async_config_entry_first_refresh()

        # Create one sensor entity per station_id for now.
        # If a station provides multiple distinct measurable values (e.g., flow, level, temp)
        # and they need to be separate HA entities, logic would be needed here to
        # inspect coordinator.data (after first_refresh) and create multiple sensors
        # each pointing to a specific key in the data.
        sensors.append(ChjSaihStationSensor(coordinator, station_id))

    if sensors:
        async_add_entities(sensors)
    else:
        LOGGER.info("No sensors were set up for CHJ SAIH for entry %s.", entry.entry_id)


class ChjSaihStationCoordinator(DataUpdateCoordinator):
    """Data coordinator for a single CHJ SAIH station."""

    def __init__(self, hass: HomeAssistant, api_client: APIClient, station_id: str, update_interval: timedelta):
        """Initialize the coordinator."""
        self.api_client = api_client
        self.station_id = station_id
        super().__init__(
            hass,
            LOGGER, # Use the integration's logger
            name=f"{DOMAIN}_station_{station_id}", # Unique name for the coordinator
            update_interval=update_interval,
        )
        LOGGER.debug(
            "Initialized coordinator for station %s with update interval %s",
            station_id, update_interval
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint for the station."""
        LOGGER.debug("Fetching data for station %s", self.station_id)
        try:
            # Assume get_station_data(station_id) returns a dict of sensor values for that station
            # e.g., {"flow": 10.5, "level": 2.1, "unit_flow": "m3/s", "unit_level": "m", "timestamp": "...",
            #         "station_name": "River Monitoring Point X", "river_name": "River Y"}
            station_data = await self.hass.async_add_executor_job(
                self.api_client.get_station_data, self.station_id
            )
            if not station_data:
                # This case might be normal if a station temporarily has no data.
                # Depending on API, it might return empty dict/list or specific no-data marker.
                LOGGER.warning("No data received for station %s", self.station_id)
                # Return empty dict or previously known data if preferred, instead of raising UpdateFailed immediately
                # For now, stick to raising UpdateFailed if no data, to mark entity unavailable.
                raise UpdateFailed(f"No data received for station {self.station_id}")

            # Optionally, add station_id to the data if not already present; useful for entities.
            if "station_id" not in station_data:
                station_data["station_id"] = self.station_id

            LOGGER.debug("Data fetched for station %s: %s", self.station_id, station_data)
            return station_data
        except SaihError as err:
            LOGGER.error("API error for station %s: %s", self.station_id, err)
            raise UpdateFailed(f"Error communicating with API for station {self.station_id}: {err}")
        except Exception as err: # pylint: disable=broad-except
            LOGGER.exception(f"Unexpected error fetching data for station {self.station_id}: {err}")
            raise UpdateFailed(f"Unexpected error for station {self.station_id}: {err}")


class ChjSaihStationSensor(CoordinatorEntity[ChjSaihStationCoordinator], SensorEntity):
    """Representation of a CHJ SAIH Station sensor."""

    # Uncomment if your HA version is new enough and you want this behavior
    # _attr_has_entity_name = True
    # This would make entity name based on device name + default name (e.g. "CHJ SAIH Station XYZ Temperature")
    # If False (default) or not set, entity name is what `name` property returns.

    def __init__(self, coordinator: ChjSaihStationCoordinator, station_id: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._station_id = station_id

        # Unique ID for the entity
        self._attr_unique_id = f"{DOMAIN}_{self._station_id}" # Main sensor for this station

        # Device Info: links this sensor to a device representing the physical station
        # Updated dynamically in _handle_coordinator_update if more details come from data
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._station_id)},
            "name": f"CHJ SAIH Station {self._station_id}", # Default name
            "manufacturer": "CHJ", # Placeholder for Confederación Hidrográfica del Júcar
            "model": "SAIH Station",
            # "via_device": (DOMAIN, coordinator.config_entry.entry_id), # If there's a central integration device
        }

        # Initial update of name and device info based on potentially already fetched data
        self._update_attrs_from_coordinator_data()


    def _update_attrs_from_coordinator_data(self):
        """Update entity attributes based on coordinator data."""
        if self.coordinator.data:
            station_name = self.coordinator.data.get(ATTR_STATION_NAME)
            if station_name:
                self._attr_device_info["name"] = station_name

            # Example: if river_name is available, add it to device model or attributes
            river_name = self.coordinator.data.get(ATTR_RIVER_NAME)
            if river_name:
                 self._attr_device_info["model"] = f"{river_name} - SAIH Station"


    @property
    def name(self) -> str:
        """Return the name of the sensor entity."""
        if self.coordinator.data and self.coordinator.data.get(ATTR_STATION_NAME):
            # If _attr_has_entity_name = True, this might form part of the name or be overridden.
            # If _attr_has_entity_name = False, this is the full entity name.
            return str(self.coordinator.data.get(ATTR_STATION_NAME))
        return f"SAIH Station {self._station_id}" # Fallback name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # CoordinatorEntity handles availability based on last_update_success and coordinator.data
        return super().available

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        # PRIMARY SENSOR VALUE LOGIC - THIS IS HIGHLY DEPENDENT ON API RESPONSE
        # Option 1: A known primary field, e.g. 'flow' or 'level'.
        # Assume for now 'flow' is primary if available, else 'level', else 'temperature'.
        # This needs to be defined based on what get_station_data returns and what makes sense.
        # Example:
        # if "flow" in self.coordinator.data:
        #     return self.coordinator.data["flow"]
        # if "level" in self.coordinator.data:
        #     return self.coordinator.data["level"]
        # if "temperature" in self.coordinator.data:
        #    return self.coordinator.data["temperature"]

        # Option 2: The problem description mentioned "Timestamp of last data point from source".
        # This could be ATTR_LAST_UPDATE if that represents the data point's timestamp.
        if ATTR_LAST_UPDATE in self.coordinator.data:
            return self.coordinator.data[ATTR_LAST_UPDATE]

        # Fallback if no specific primary value identified or ATTR_LAST_UPDATE is not present
        return "Online" # Or count of data points: len(self.coordinator.data)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement for the sensor's state."""
        if not self.coordinator.data:
            return None

        # Must correspond to the logic in native_value.
        # Example matching Option 1 above:
        # if "flow" in self.coordinator.data and "unit_flow" in self.coordinator.data:
        #     return self.coordinator.data["unit_flow"]
        # if "level" in self.coordinator.data and "unit_level" in self.coordinator.data:
        #     return self.coordinator.data["unit_level"]
        # if "temperature" in self.coordinator.data and "unit_temp" in self.coordinator.data:
        #    return self.coordinator.data["unit_temp"]

        # If native_value is ATTR_LAST_UPDATE (a timestamp string) or "Online", unit is None.
        return None

    @property
    def extra_state_attributes(self):
        """Return other state attributes of the entity."""
        if not self.coordinator.data:
            return {}

        # Exclude keys already used for primary state, name, or device identifiers.
        # Or, explicitly pick attributes to expose.
        excluded_keys = {
            "station_id", # Already in unique_id and device_info identifiers
            ATTR_STATION_NAME, # Used for name/device name
            # If native_value uses 'flow', exclude 'flow' and 'unit_flow' here.
            # For now, if native_value is ATTR_LAST_UPDATE or "Online", we can expose most other things.
            ATTR_LAST_UPDATE if self.native_value == self.coordinator.data.get(ATTR_LAST_UPDATE) else None,
        }

        attrs = {
            key: value
            for key, value in self.coordinator.data.items()
            if key not in excluded_keys and value is not None
        }
        # Ensure station_id is present if not already by some other name
        attrs["station_code"] = self._station_id # Use a different key like "station_code" to avoid conflict
        return attrs

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_attrs_from_coordinator_data()
        super()._handle_coordinator_update()

```
