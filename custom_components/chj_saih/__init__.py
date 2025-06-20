"""The CHJ SAIH Integration."""
# Home Assistant core & const
from homeassistant.config_entries import ConfigEntry
# from homeassistant.const import CONF_SCAN_INTERVAL # Not directly used by __init__.py logic
from homeassistant.core import HomeAssistant

# Local
from .const import (
    DOMAIN,
    LOGGER,
    PLATFORMS,
    # CONF_STATIONS, # Not directly used by logic in __init__.py, but part of data structure
    # Other CONF_ constants are part of entry.data, not directly used by __init__.py
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CHJ SAIH from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Store a copy of the entry data in hass.data for access by platforms.
    # This includes all configuration keys like CONF_STATIONS, CONF_SCAN_INTERVAL, etc.,
    # as defined in the config flow and stored in entry.data.
    hass.data[DOMAIN][entry.entry_id] = dict(entry.data)

    LOGGER.debug(
        "Setting up entry %s with data: %s", entry.entry_id, entry.data
    )

    # Register update listener for options flow
    entry.add_update_listener(async_update_options)

    # Forward the setup to platforms. PLATFORMS is defined in const.py.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    LOGGER.debug("Unloading entry %s", entry.entry_id)

    # Forward the unloading of the entry to platforms.
    unload_ok = await hass.config_entries.async_forward_entry_unloads(entry, PLATFORMS)

    if unload_ok:
        # Clean up hass.data
        hass.data[DOMAIN].pop(entry.entry_id)
        LOGGER.info("Successfully unloaded entry %s", entry.entry_id)
        if not hass.data[DOMAIN]: # If no more entries for this domain
            hass.data.pop(DOMAIN) # Clean up the domain from hass.data

    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update by reloading the entry."""
    LOGGER.debug("Configuration options updated for %s, reloading entry.", entry.entry_id)
    await hass.config_entries.async_reload(entry.entry_id)

# Example for future:
# async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
#    """Migrate old entry."""
#    LOGGER.debug("Migrating from version %s", config_entry.version)
#    # Migration logic here
#    return True
