"""Constants for the LIFAair integration."""

DOMAIN = "lifaair"
DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = 30

CONF_HOST = "host"

DEVTYPE_LIFAAIR = 0x4EC2

ATTR_TEMPERATURE = "temperature"
ATTR_HUMIDITY = "humidity"
ATTR_CO2 = "co2"
ATTR_TVOC = "tvoc"
ATTR_PM1 = "pm1"
ATTR_PM25 = "pm2_5"
ATTR_PM10 = "pm10"
ATTR_FAN_MODE = "fan_mode"
ATTR_FAN_SPEED = "fan_speed"

PRESET_OFF = "off"
PRESET_AUTO = "auto"
PRESET_NIGHT = "night"
PRESET_TURBO = "turbo"
PRESET_ANTI_ALLERGY = "anti_allergy"
PRESET_MANUAL = "manual"

PRESET_MODES = (
    PRESET_AUTO,
    PRESET_NIGHT,
    PRESET_TURBO,
    PRESET_ANTI_ALLERGY,
    PRESET_MANUAL,
)
