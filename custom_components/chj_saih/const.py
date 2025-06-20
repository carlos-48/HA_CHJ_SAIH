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
CF_SCAN_INTERVAL_LISTENER = "scan_interval_listener"

# Configuration types
CONF_CONFIG_TYPE = "config_type"
CONF_STATION_ID_INPUT = "station_id_input"
CONF_RADIUS = "radius"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_SENSOR_TYPES_INPUT = "sensor_types_input"
SENSOR_TYPES_OPTIONS = ["RainGauge", "Flow", "Reservoir", "Temperature"]
