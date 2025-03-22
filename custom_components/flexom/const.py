"""Constants for Flexom integration."""
from typing import Final

DOMAIN: Final = "flexom"

# Configuration
CONF_USERNAME: Final = "username"
CONF_PASSWORD: Final = "password"

# API URLs
HEMISPHERE_URL: Final = "https://hemisphere.ubiant.com"
HEMISPHERE_SIGNIN_URL: Final = "/users/signin"
HEMISPHERE_BUILDINGS_URL: Final = "/buildings/mine/infos"
HEMIS_BASE_URL_TEMPLATE: Final = "https://{}.{}.hemis.io/hemis/rest"

# WebSocket topics
STOMP_TOPIC_DATA: Final = "jms.topic.{building_id}.data"
STOMP_TOPIC_MANAGEMENT: Final = "jms.topic.{building_id}.management"

# Factors
FACTOR_BRIGHTNESS: Final = "BRI"  # Luminosité
FACTOR_BRIGHTNESS_EXT: Final = "BRIEXT"  # Occultation (volets)
FACTOR_TEMPERATURE: Final = "TMP"  # Température

# WebSocket message types
WS_TYPE_ACTUATOR_TARGET_STATE: Final = "ACTUATOR_TARGET_STATE"
WS_TYPE_ACTUATOR_HARDWARE_STATE: Final = "ACTUATOR_HARDWARE_STATE"
WS_TYPE_ACTUATOR_CURRENT_STATE: Final = "ACTUATOR_CURRENT_STATE"
WS_TYPE_SENSOR_STATE: Final = "SENSOR_STATE"
WS_TYPE_IT_STATE: Final = "IT_STATE"
WS_TYPE_FACTOR_TARGET_STATE: Final = "FACTOR_TARGET_STATE"
WS_TYPE_FACTOR_CURRENT_STATE: Final = "FACTOR_CURRENT_STATE"
