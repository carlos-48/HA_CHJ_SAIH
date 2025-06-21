"""The CHJ SAIH integration."""
from __future__ import annotations

from datetime import timedelta # Added

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
# ConfigEntryNotReady might be needed if we want to raise it explicitly
# from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    DOMAIN,
    PLATFORMS,
    CONF_STATIONS,
    LOGGER,
    # CF_SCAN_INTERVAL_LISTENER, # No longer needed here
)
from .coordinator import ChjSaihDataUpdateCoordinator # Added


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CHJ SAIH from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    station_ids = entry.data[CONF_STATIONS]
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL)
    )

    LOGGER.info(
        "Setting up CHJ SAIH integration for stations %s with scan interval %s seconds",
        station_ids,
        scan_interval,
    )

    coordinator = ChjSaihDataUpdateCoordinator(
        hass,
        station_ids=station_ids,
        update_interval=timedelta(seconds=scan_interval),
    )

    await coordinator.async_config_entry_first_refresh()
    # If async_config_entry_first_refresh raises UpdateFailed (which it does on errors),
    # Home Assistant will retry the setup later. ConfigEntryNotReady can also be raised here.

    hass.data[DOMAIN][entry.entry_id] = {
        CONF_STATIONS: station_ids, # May be removed if sensors get it from coordinator/entry
        CONF_SCAN_INTERVAL: scan_interval, # May be removed if sensors get it from coordinator/entry
        "coordinator": coordinator,
    }

    # Set up listener for options changes, automatically cleaned up on unload
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # Forward the setup to platforms.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    LOGGER.debug("CHJ SAIH integration setup complete for entry %s", entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    LOGGER.info("Unloading CHJ SAIH integration for entry %s", entry.entry_id)

    # Unload platforms.
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Listener is automatically removed by entry.async_on_unload

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        LOGGER.debug("CHJ SAIH integration successfully unloaded for entry %s", entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle an options update."""
    LOGGER.debug("Reloading CHJ SAIH integration for entry %s due to options update", entry.entry_id)
    await hass.config_entries.async_reload(entry.entry_id)
    # async_unload_entry and async_setup_entry will be called automatically by HA
