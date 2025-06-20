# Standard library
from datetime import timedelta

# Third-party
from chj_saih import APIClient
from chj_saih.exceptions import SaihError

# Home Assistant core, components, const
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL # Used for entry_data key
from homeassistant.core import HomeAssistant

# Home Assistant helpers
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

# Local
from .const import (
    ATTR_LAST_UPDATE,
    ATTR_RIVER_NAME,
    ATTR_STATION_NAME,
    CONF_STATIONS, # Used for entry_data key
    DOMAIN,
    LOGGER,
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
    scan_interval_seconds = entry_data[CONF_SCAN_INTERVAL] # Key from .const via config_flow

    if not station_ids:
        LOGGER.warning("No station IDs configured for CHJ SAIH for entry %s.", entry.entry_id)
        return

    api_client = APIClient()

    sensors = []
    for station_id in station_ids:
        coordinator = ChjSaihStationCoordinator(
            hass,
            api_client,
            station_id,
            timedelta(seconds=scan_interval_seconds),
        )
        await coordinator.async_config_entry_first_refresh()

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
            LOGGER,
            name=f"{DOMAIN}_station_{station_id}",
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
            station_data = await self.hass.async_add_executor_job(
                self.api_client.get_station_data, self.station_id
            )
            if not station_data:
                LOGGER.warning("No data received for station %s", self.station_id)
                raise UpdateFailed(f"No data received for station {self.station_id}")

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

    # _attr_has_entity_name = True

    def __init__(self, coordinator: ChjSaihStationCoordinator, station_id: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._station_id = station_id
        self._attr_unique_id = f"{DOMAIN}_{self._station_id}"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._station_id)},
            "name": f"CHJ SAIH Station {self._station_id}",
            "manufacturer": "CHJ",
            "model": "SAIH Station",
        }

        self._update_attrs_from_coordinator_data()


    def _update_attrs_from_coordinator_data(self):
        """Update entity attributes based on coordinator data."""
        if self.coordinator.data:
            station_name = self.coordinator.data.get(ATTR_STATION_NAME)
            if station_name:
                self._attr_device_info["name"] = station_name

            river_name = self.coordinator.data.get(ATTR_RIVER_NAME)
            if river_name:
                 self._attr_device_info["model"] = f"{river_name} - SAIH Station"


    @property
    def name(self) -> str:
        """Return the name of the sensor entity."""
        if self.coordinator.data and self.coordinator.data.get(ATTR_STATION_NAME):
            return str(self.coordinator.data.get(ATTR_STATION_NAME))
        return f"SAIH Station {self._station_id}"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        if ATTR_LAST_UPDATE in self.coordinator.data:
            return self.coordinator.data[ATTR_LAST_UPDATE]

        return "Online"

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement for the sensor's state."""
        if not self.coordinator.data:
            return None
        return None

    @property
    def extra_state_attributes(self):
        """Return other state attributes of the entity."""
        if not self.coordinator.data:
            return {}

        excluded_keys = {
            "station_id",
            ATTR_STATION_NAME,
            ATTR_LAST_UPDATE if self.native_value == self.coordinator.data.get(ATTR_LAST_UPDATE) else None,
        }

        attrs = {
            key: value
            for key, value in self.coordinator.data.items()
            if key not in excluded_keys and value is not None
        }
        attrs["station_code"] = self._station_id
        return attrs

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_attrs_from_coordinator_data()
        super()._handle_coordinator_update()
