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

# Power profiles mapping
POWER_PROFILES = {
    "max_power": {"name": "Max Power", "overclock": 2, "description": "+2 overclock profile for peak performance"},
    "balanced": {"name": "Balanced", "overclock": 0, "description": "Default profile for optimal efficiency"},
    "ultra_eco": {"name": "Ultra Eco", "overclock": -2, "description": "-2 underclock profile for minimal power consumption"},
    "night_30": {"name": "Night Mode (30%)", "overclock": -8, "description": "30% power for quiet night operation"},
    "night_15": {"name": "Night Mode (15%)", "overclock": -12, "description": "15% power for ultra-quiet operation"},
    "standby": {"name": "Standby", "overclock": -16, "description": "Minimum power standby mode"}
}

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