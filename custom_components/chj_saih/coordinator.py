import async_timeout
from datetime import datetime, timedelta
import logging # Use LOGGER from .const instead if preferred globally
import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from chj_saih import fetch_sensor_data # Assuming this is the correct import path

from .const import DOMAIN, LOGGER, ATTR_LAST_UPDATE # Import necessary constants

class ChjSaihDataUpdateCoordinator(DataUpdateCoordinator[dict[str, dict]]):
    """Class to manage fetching CHJ SAIH data from API."""

    def __init__(
        self,
        hass: HomeAssistant,
        station_ids: list[str],
        update_interval: timedelta,
    ) -> None:
        """Initialize."""
        self.station_ids = station_ids
        self._hass = hass # Store hass if needed for other purposes, like translations

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, dict]:
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        LOGGER.debug("Fetching data for stations: %s", self.station_ids)
        session = async_get_clientsession(self._hass)
        all_station_data_processed: dict[str, dict] = {}

        try:
            # Using async_timeout ensures the entire update process doesn't hang indefinitely.
            # Adjust timeout as needed, e.g., 30 seconds per station or a total timeout.
            # For simplicity, a total timeout for all stations:
            async with async_timeout.timeout(30 * len(self.station_ids) if self.station_ids else 30):
                for station_id in self.station_ids:
                    try:
                        LOGGER.debug("Fetching data for station_id: %s", station_id)
                        raw_data = await fetch_sensor_data(variable=station_id, session=session)

                        if not isinstance(raw_data, list) or len(raw_data) != 3:
                            LOGGER.warning(
                                "Unexpected data structure for station %s: %s",
                                station_id,
                                raw_data
                            )
                            # Store error or empty data for this station
                            all_station_data_processed[station_id] = {"error": "unexpected_data_structure"}
                            continue

                        data_info = raw_data[0]
                        readings_list = raw_data[1]

                        if not readings_list: # No readings available
                            LOGGER.info("No readings available for station %s.", station_id)
                            all_station_data_processed[station_id] = {
                                "value": None,
                                "name": data_info.get('descripcion', f"CHJ SAIH {station_id}"),
                                "unit": data_info.get('dimension') or data_info.get('tipoVariable', {}).get('unidades'),
                                ATTR_LAST_UPDATE: None,
                                "error": "no_readings",
                                "metadata": data_info, # Still provide metadata
                            }
                            continue

                        # Assume first reading is the most recent
                        latest_reading = readings_list[0]
                        timestamp_str, value_str = latest_reading[0], latest_reading[1]

                        parsed_value = None
                        try:
                            parsed_value = float(value_str)
                        except (ValueError, TypeError):
                            LOGGER.warning(
                                "Could not parse value '%s' for station %s", value_str, station_id
                            )
                            all_station_data_processed[station_id] = {
                                "error": "value_parse_error",
                                "name": data_info.get('descripcion', f"CHJ SAIH {station_id}"),
                                "unit": data_info.get('dimension') or data_info.get('tipoVariable', {}).get('unidades'),
                                "metadata": data_info,
                            }
                            continue

                        parsed_timestamp = None
                        try:
                            dt_object = datetime.strptime(timestamp_str, '%d/%m/%Y %H:%M')
                            # It's good practice to store datetimes in UTC in Home Assistant if possible,
                            # or ensure they are timezone-aware. If the API provides naive datetimes,
                            # Home Assistant will typically treat them as local system time.
                            # For now, store as ISO string.
                            parsed_timestamp = dt_object.isoformat()
                        except (ValueError, TypeError):
                            LOGGER.warning(
                                "Could not parse timestamp '%s' for station %s", timestamp_str, station_id
                            )
                            # Continue processing, but timestamp will be missing or None

                        all_station_data_processed[station_id] = {
                            "value": parsed_value,
                            "name": data_info.get('descripcion', f"CHJ SAIH {station_id}"),
                            "unit": data_info.get('dimension') or data_info.get('tipoVariable', {}).get('unidades'),
                            ATTR_LAST_UPDATE: parsed_timestamp,
                            "metadata": data_info, # Store all metadata for potential use by entities
                        }
                        LOGGER.debug("Successfully processed data for station_id: %s", station_id)

                    except aiohttp.ClientError as err:
                        LOGGER.warning("Error fetching data for station %s: %s", station_id, err)
                        all_station_data_processed[station_id] = {"error": "client_error", "details": str(err)}
                        # Optionally, re-raise if one station failure should fail all:
                        # raise UpdateFailed(f"Failed to fetch data for station {station_id}: {err}") from err
                    except Exception as err:
                        LOGGER.exception(
                            "Unexpected error processing data for station %s: %s", station_id, err
                        )
                        all_station_data_processed[station_id] = {"error": "unknown", "details": str(err)}
                        # Optionally, re-raise:
                        # raise UpdateFailed(f"Unexpected error for station {station_id}: {err}") from err

            if not all_station_data_processed and self.station_ids: # If all stations failed and there were stations to fetch
                LOGGER.warning("No data successfully processed for any station.")
                # Raise UpdateFailed if no station data could be retrieved and stations were configured.
                # This helps in identifying a widespread issue vs. individual station problems.
                raise UpdateFailed("Failed to process data for any configured station.")


            return all_station_data_processed

        except async_timeout.TimeoutError:
            LOGGER.error("Timeout occurred while fetching CHJ SAIH data")
            raise UpdateFailed("Timeout occurred while fetching CHJ SAIH data")
        except Exception as err: # Catch-all for unexpected errors during setup or overall process
            LOGGER.exception("Unhandled error in CHJ SAIH data update: %s", err)
            raise UpdateFailed(f"Unhandled error in CHJ SAIH data update: {err}")
