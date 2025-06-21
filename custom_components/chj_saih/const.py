"""Constants for the CHJ SAIH integration."""
from logging import getLogger

LOGGER = getLogger(__package__)

DOMAIN = "chj_saih"

DEFAULT_SCAN_INTERVAL = 1800  # seconds
CONF_STATIONS = "stations"

# Platforms
SENSOR = "sensor"
PLATFORMS = [SENSOR]

# Attributes
ATTR_LAST_UPDATE = "last_update"
ATTR_DATA_URL = "data_url"
ATTR_RIVER_NAME = "river_name"
ATTR_STATION_NAME = "station_name"
ATTR_STATION_ID = "station_id"

# Config Flow
