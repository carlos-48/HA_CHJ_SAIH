"""Config flow for CHJ SAIH."""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession # Added
import homeassistant.helpers.config_validation as cv
import aiohttp # Added

from chj_saih import fetch_all_stations # Added

from .const import (
    CONF_STATIONS,  # Added
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
)


class ChjSaihConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CHJ SAIH."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return ChjSaihOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}  # Added
        # if self._async_current_entries(): # Removed
        #     return self.async_abort(reason="single_instance_allowed") # Removed

        if user_input is not None:
            try:
                stations_str = user_input[CONF_STATIONS]
                # Clean and split, removing empty strings from "id1,,id2"
                station_ids_input = [s.strip() for s in stations_str.split(',') if s.strip()]

                if not station_ids_input:
                    errors[CONF_STATIONS] = "empty_station_list"
                else:
                    session = async_get_clientsession(self.hass)
                    all_stations_data = await fetch_all_stations(session=session)

                    valid_station_ids_from_api = {
                        station['variable'] for station in all_stations_data if 'variable' in station
                    }

                    invalid_user_stations = [
                        sid for sid in station_ids_input if sid not in valid_station_ids_from_api
                    ]

                    if invalid_user_stations:
                        LOGGER.error(f"Invalid station IDs entered: {invalid_user_stations}")
                        errors["base"] = "invalid_station_id"
                        # For more specific feedback, you could add to errors[CONF_STATIONS]
                        # errors[CONF_STATIONS] = f"The following station IDs are invalid: {', '.join(invalid_user_stations)}"
                    else:
                        # All stations are valid, store the cleaned list
                        user_input[CONF_STATIONS] = station_ids_input
                        LOGGER.info(f"Configuring CHJ SAIH with stations: {user_input[CONF_STATIONS]}")
                        return self.async_create_entry(title="CHJ SAIH", data=user_input)

            except aiohttp.ClientError as e:
                LOGGER.error(f"Error connecting to CHJ SAIH service: {e}")
                errors["base"] = "cannot_connect"
            except Exception as e: # Catch any other unexpected errors during validation
                LOGGER.exception(f"Unexpected error validating stations: {e}")
                errors["base"] = "unknown_error"

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_STATIONS, default=""
                ): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): cv.positive_int,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors  # Modified
        )


class ChjSaihOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for CHJ SAIH."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            LOGGER.debug(
                "Updating entry %s with options: %s",
                self.config_entry.title,
                user_input,
            )
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): cv.positive_int,
                }
            ),
        )
