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
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="CHJ SAIH", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): cv.positive_int,
                }
            ),
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
