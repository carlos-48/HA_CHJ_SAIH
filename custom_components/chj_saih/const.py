"""Constants for the CHJ SAIH integration."""
from logging import getLogger

LOGGER = getLogger(__package__)

DOMAIN = "chj_saih"

DEFAULT_SCAN_INTERVAL = 1800  # seconds

# General Configuration Keys
CONF_STATIONS = "stations"
# CONF_SCAN_INTERVAL is defined in homeassistant.const, but we use the string "scan_interval"
# as a key in config flows and data dictionaries. This can also be defined here if needed
# to ensure consistency, e.g. CONF_SCAN_INTERVAL_KEY = "scan_interval".
# For now, relying on direct string or HA's CONF_SCAN_INTERVAL where appropriate.

# Platforms
SENSOR = "sensor"
PLATFORMS = [SENSOR]

# Attributes
ATTR_LAST_UPDATE = "last_update"
ATTR_DATA_URL = "data_url"
ATTR_RIVER_NAME = "river_name"
ATTR_STATION_NAME = "station_name"
ATTR_STATION_ID = "station_id" # Used for individual station identification

# Config Flow
CF_SCAN_INTERVAL_LISTENER = "scan_interval_listener" # Example, not currently used actively

# Configuration step keys / types
CONF_CONFIG_TYPE = "config_type" # User's choice: "single" or "radius"
CONF_STATION_ID_INPUT = "station_id_input" # For single station ID input
CONF_RADIUS = "radius" # For radius search
CONF_LATITUDE = "latitude"   # Individual latitude, potentially for internal use or older configs
CONF_LONGITUDE = "longitude" # Individual longitude, potentially for internal use or older configs
CONF_LOCATION = "location"   # For combined location input (map selector)
CONF_SENSOR_TYPES_INPUT = "sensor_types_input" # For selecting sensor types in radius search
SENSOR_TYPES_OPTIONS = ["RainGauge", "Flow", "Reservoir", "Temperature"] # Options for multi-select

# Note: CONF_SCAN_INTERVAL from homeassistant.const is used in schemas,
# while the string "scan_interval" is used as a key in init_data.
# If a constant is needed for the key:
# SCAN_INTERVAL_KEY = "scan_interval"
# This is managed by using .const.CONF_SCAN_INTERVAL in config_flow.py for dict keys.
# And homeassistant.const.CONF_SCAN_INTERVAL (aliased) for Voluptuous schema.
