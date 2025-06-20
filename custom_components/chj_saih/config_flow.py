"""Config flow for CHJ SAIH."""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
    CONF_CONFIG_TYPE,
    CONF_STATION_ID_INPUT,
    CONF_LATITUDE,
    CONF_LONGITUDE, # Will be indirectly used via CONF_LOCATION in future steps
    CONF_RADIUS,
    CONF_SENSOR_TYPES_INPUT,
    SENSOR_TYPES_OPTIONS,
    CONF_STATIONS,
    CONF_LOCATION, # New constant for location selector
)
from homeassistant.helpers import selector # For location selector


# Assuming APIClient and SaihError are structured like this in the library
# If the library is part of the integration (e.g. in a `pychj_saih` subfolder),
# the import path might be different, e.g. `from .pychj_saih import APIClient`.
# For now, following the problem description:
from chj_saih import APIClient
from chj_saih.exceptions import SaihError


class ChjSaihConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CHJ SAIH."""

    VERSION = 1
    # init_data can be initialized here if it needs to persist across different instantiations
    # of the flow, but typically it's better to manage it as an instance variable.
    # For this use case, self.init_data will be initialized as needed.

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return ChjSaihOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # Prevent multiple instances of the integration unless it's a reconfigure flow
        if self._async_current_entries(include_ignore=False):
             return self.async_abort(reason="single_instance_allowed")

        errors = {}

        if user_input is not None:
            # Ensure init_data is initialized for this flow instance
            if not hasattr(self, 'init_data'):
                self.init_data = {}
            self.init_data.update(user_input) # Store user input
            config_type = user_input[CONF_CONFIG_TYPE]
            if config_type == "single":
                return await self.async_step_single_station()
            elif config_type == "radius":
                return await self.async_step_radius_search()
            # Not expecting other cases due to vol.In validation

        # Initial form or if there was an issue (though vol.In should prevent type errors)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CONFIG_TYPE): vol.In(
                        {
                            "single": "Single Station",
                            "radius": "Stations by Radius",
                        }
                    )
                }
            ),
            errors=errors,
        )

    async def async_step_single_station(self, user_input=None):
        """Handle the single station configuration step."""
        errors = {}
        if user_input is not None:
            # Ensure init_data is initialized (should be by async_step_user)
            if not hasattr(self, 'init_data'):
                self.init_data = {} # Should ideally not happen if flow starts from user step
            self.init_data[CONF_STATION_ID_INPUT] = user_input[CONF_STATION_ID_INPUT]
            # No validation for now, proceed to next step
            return await self.async_step_configure_global()

        # Show form to get station ID
        return self.async_show_form(
            step_id="single_station",
            data_schema=vol.Schema(
                {vol.Required(CONF_STATION_ID_INPUT): str}
            ),
            errors=errors,
            description_placeholders={"docs_url": "URL_TO_STATION_ID_DOCS_OR_INFO"}, # Example placeholder
        )

    async def async_step_radius_search(self, user_input=None):
        """Handle the radius search configuration step."""
        errors = {}
        if user_input is not None:
            # Ensure init_data is initialized (should be by async_step_user)
            if not hasattr(self, 'init_data'):
                self.init_data = {} # Should ideally not happen if flow starts from user step

            # Clear old lat/lon if they existed from a previous version or different logic
            self.init_data.pop(CONF_LATITUDE, None)
            self.init_data.pop(CONF_LONGITUDE, None)

            self.init_data[CONF_LOCATION] = user_input[CONF_LOCATION]
            self.init_data[CONF_RADIUS] = user_input[CONF_RADIUS] # RADIUS is optional, so might not be in user_input if not changed from default
            self.init_data[CONF_SENSOR_TYPES_INPUT] = user_input[CONF_SENSOR_TYPES_INPUT]

            # The temporary lines for CONF_LATITUDE and CONF_LONGITUDE direct assignment are now removed.
            # async_step_configure_global will now read from CONF_LOCATION directly.

            return await self.async_step_configure_global()

        # Show form to get radius search parameters
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_LOCATION,
                    default={ # Default to HA's configured home location
                        "latitude": self.hass.config.latitude,
                        "longitude": self.hass.config.longitude,
                    }
                ): selector.selector({"location": {}}), # Location selector
                vol.Optional(
                    CONF_RADIUS,
                    default=50 # Default radius 50km
                ): cv.positive_float,
                vol.Required(CONF_SENSOR_TYPES_INPUT): cv.multi_select(
                    SENSOR_TYPES_OPTIONS
                ),
            }
        )
        return self.async_show_form(
            step_id="radius_search", data_schema=data_schema, errors=errors
        )

    async def async_step_configure_global(self, user_input=None):
        """Handle global configuration like scan interval and finalize entry creation."""
        errors = {}
        # Ensure init_data is initialized (it should be by previous steps)
        if not hasattr(self, 'init_data'):
            # This case should ideally not be reached if the flow starts from async_step_user
            self.init_data = {}
            # Potentially abort or redirect to user step if init_data is missing crucial parts
            # For now, assume it's populated by previous steps.

        if user_input is not None:
            self.init_data[CONF_SCAN_INTERVAL] = user_input[CONF_SCAN_INTERVAL]
            config_type = self.init_data.get(CONF_CONFIG_TYPE)

            if config_type == "radius":
                try:
                    location_data = self.init_data[CONF_LOCATION]
                    lat = location_data['latitude']
                    lon = location_data['longitude']
                    radius = self.init_data[CONF_RADIUS]
                    sensor_types = self.init_data[CONF_SENSOR_TYPES_INPUT]

                    # Ensure APIClient can be instantiated correctly
                    # This might need hass passed or other setup if it's complex.
                    client = APIClient()

                    LOGGER.debug(
                        "Fetching stations by radius: radius=%s, types=%s",
                        radius, sensor_types
                    )
                    # Assuming get_stations_by_radius is a blocking call
                    stations_data = await self.hass.async_add_executor_job(
                        client.get_stations_by_radius, lat, lon, radius, sensor_types
                    )

                    if stations_data:
                        # Assuming stations_data is a list of dicts with 'id' key
                        station_ids = [s["id"] for s in stations_data if "id" in s]
                        if station_ids:
                            self.init_data[CONF_STATIONS] = station_ids
                            LOGGER.info("Found stations by radius: %s", station_ids)
                        else:
                            LOGGER.warning("No station IDs found in data: %s", stations_data)
                            errors["base"] = "no_stations_found_data"
                    else:
                        LOGGER.warning("No stations found for the given radius criteria.")
                        errors["base"] = "no_stations_found"

                except SaihError as e:
                    LOGGER.error("API error during radius search: %s", e)
                    errors["base"] = "radius_search_api_error" # Or more specific like "cannot_connect"
                except Exception as e:  # pylint: disable=broad-except
                    LOGGER.exception("Unexpected error during radius search: %s", e)
                    errors["base"] = "unknown_error_radius"

            elif config_type == "single":
                station_id = self.init_data.get(CONF_STATION_ID_INPUT)
                if station_id:
                    self.init_data[CONF_STATIONS] = [station_id]
                    # Optional: Add validation for single station ID here if desired
                    # For example, by trying to fetch station details.
                    # If fails: errors[CONF_STATION_ID_INPUT] = "invalid_station_id"
                else:
                    # This should not happen if previous steps worked correctly
                    errors["base"] = "missing_station_id"

            else:
                # Should not happen due to initial CONF_CONFIG_TYPE validation
                LOGGER.error("Unknown config type: %s", config_type)
                errors["base"] = "unknown_config_type"

            if not errors:
                LOGGER.debug("Configuration data ready: %s", self.init_data)
                return self.async_create_entry(title=DOMAIN, data=self.init_data)

        # Show form for scan interval (initial display or if errors occurred)
        return self.async_show_form(
            step_id="configure_global",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.init_data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                    ): cv.positive_int,
                }
            ),
            errors=errors,
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
