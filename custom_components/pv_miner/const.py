"""Constants for the PV Miner integration."""

DOMAIN = "pv_miner"

# Configuration
CONF_HOST = "host"
CONF_NAME = "name"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_SOLAR_SCAN_INTERVAL = "solar_scan_interval"
CONF_MIN_POWER = "min_power"
CONF_MAX_POWER = "max_power"
CONF_PRIORITY = "priority"

# Default values
DEFAULT_USERNAME = "root"
DEFAULT_PASSWORD = "root"
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_SOLAR_SCAN_INTERVAL = 600  # 10 minutes
DEFAULT_MIN_POWER = 500
DEFAULT_MAX_POWER = 4200

# LuxOS API endpoints
LUXOS_LOGIN_ENDPOINT = "/cgi-bin/luxcgi"
LUXOS_API_ENDPOINT = "/cgi-bin/luxcgi"

# Power profiles are now loaded dynamically from the miner via LuxOS API
# No fixed POWER_PROFILES constant needed - profiles are discovered at runtime

# Solar operation modes
SOLAR_MODES = {
    "manual": "Manual Power Input",
    "auto": "Automatic Solar Tracking",
    "sun_curve": "Sun Curve Mode",
    "peak_solar": "Peak Solar Mode (120%)"
}

# Entity types
SENSOR_TYPES = {
    "hashrate": {"name": "Hashrate", "unit": "TH/s", "icon": "mdi:chip"},
    "power": {"name": "Power Consumption", "unit": "W", "icon": "mdi:flash"},
    "temperature": {"name": "Temperature", "unit": "°C", "icon": "mdi:thermometer"},
    "fan_speed": {"name": "Fan Speed", "unit": "RPM", "icon": "mdi:fan"},
    "efficiency": {"name": "Efficiency", "unit": "J/TH", "icon": "mdi:gauge"},
    "uptime": {"name": "Uptime", "unit": "s", "icon": "mdi:clock"},
    "pool": {"name": "Mining Pool", "icon": "mdi:pool"}
}

SWITCH_TYPES = {
    "miner_enabled": {"name": "Miner", "icon": "mdi:pickaxe"},
    "hashboard_0": {"name": "Hashboard 0", "icon": "mdi:chip"},
    "hashboard_1": {"name": "Hashboard 1", "icon": "mdi:chip"},
    "hashboard_2": {"name": "Hashboard 2", "icon": "mdi:chip"}
}

# Services
SERVICE_SET_POWER_PROFILE = "set_power_profile"
SERVICE_SET_POWER_LIMIT = "set_power_limit"
SERVICE_EMERGENCY_STOP = "emergency_stop"
SERVICE_SOLAR_MAX = "solar_max"
SERVICE_ECO_MODE = "eco_mode"
SERVICE_SET_POOL = "set_pool"
SERVICE_SLEEP_MINER = "sleep_miner"
SERVICE_WAKE_MINER = "wake_miner"

# Notification types
NOTIFICATION_ERROR = "pv_miner_error"
NOTIFICATION_WARNING = "pv_miner_warning"
NOTIFICATION_INFO = "pv_miner_info"