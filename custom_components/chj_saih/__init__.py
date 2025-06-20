"""The CHJ SAIH Integration."""
import asyncio

from homeassistant.core import HomeAssistant, ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.helpers.typing import HomeAssistantType

from .const import (
    DOMAIN,
    LOGGER,
    PLATFORMS,  # Contains SENSOR
    SENSOR,     # Explicitly SENSOR = "sensor"
    CONF_STATIONS,
    CONF_CONFIG_TYPE,
    CONF_STATION_ID_INPUT,
    CONF_RADIUS,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_SENSOR_TYPES_INPUT,
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CHJ SAIH from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Store a copy of the entry data in hass.data for access by platforms
    # This includes CONF_STATIONS, CONF_SCAN_INTERVAL, CONF_CONFIG_TYPE,
    # and other specific config data like CONF_STATION_ID_INPUT or radius params.
    # No sensitive data is assumed to be in entry.data at this point.
    hass.data[DOMAIN][entry.entry_id] = dict(entry.data)

    LOGGER.debug(
        "Setting up entry %s with data: %s", entry.entry_id, entry.data
    )

    # Register update listener for options flow
    entry.add_update_listener(async_update_options)

    # Forward the setup to platforms.
    # PLATFORMS should be a list of strings, e.g., ["sensor", "binary_sensor"]
    # If SENSOR is defined as "sensor", and PLATFORMS = [SENSOR], this is correct.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    LOGGER.debug("Unloading entry %s", entry.entry_id)

    # Forward the unloading of the entry to platforms.
    unload_ok = await hass.config_entries.async_forward_entry_unloads(entry, PLATFORMS)

    if unload_ok:
        # Remove options_update_listener.
        # Listeners are managed by ConfigEntry, typically no manual removal needed here for add_update_listener
        # hass.data[DOMAIN][entry.entry_id].pop(CF_SCAN_INTERVAL_LISTENER, None) # Example if we had manual listeners

        # Clean up hass.data
        hass.data[DOMAIN].pop(entry.entry_id)
        LOGGER.info("Successfully unloaded entry %s", entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN) # Clean up domain if no more entries

    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    LOGGER.debug("Configuration options updated for %s, reloading entry", entry.entry_id)
    await hass.config_entries.async_reload(entry.entry_id)

# It's good practice to also define async_migrate_entry if versioning might change config structure
# async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
#    LOGGER.debug("Migrating from version %s", config_entry.version)
#    # Migration logic
#    return True
# For now, not explicitly requested.
