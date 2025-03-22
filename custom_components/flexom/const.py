"""Constants for the Flexom integration."""
from typing import Final

DOMAIN: Final = "flexom"
HEMISPHERE_URL: Final = "https://hemisphere.ubiant.com"
HEMISPHERE_SIGNIN_URL: Final = f"{HEMISPHERE_URL}/users/signin"
HEMISPHERE_BUILDINGS_URL: Final = f"{HEMISPHERE_URL}/buildings/mine/infos"
HEMIS_BASE_URL_TEMPLATE: Final = "https://{building_id}.eu-west.hemis.io/hemis/rest"

# Configuration
CONF_USERNAME: Final = "username"
CONF_PASSWORD: Final = "password"
CONF_BUILDING_ID: Final = "building_id"
CONF_TOKEN: Final = "token"
CONF_HEMISPHERE_TOKEN: Final = "hemisphere_token"

# Factors
FACTOR_BRIGHTNESS: Final = "BRI"  # Luminosité
FACTOR_BRIGHTNESS_EXT: Final = "BRIEXT"  # Occultation (volets)
FACTOR_TEMPERATURE: Final = "TMP"  # Température

# WebSocket
STOMP_TOPIC_DATA: Final = "jms.topic.{building_id}.data"

# Websocket message types
WS_TYPE_ACTUATOR_TARGET_STATE: Final = "ACTUATOR_TARGET_STATE"
WS_TYPE_ACTUATOR_HARDWARE_STATE: Final = "ACTUATOR_HARDWARE_STATE"
WS_TYPE_ACTUATOR_CURRENT_STATE: Final = "ACTUATOR_CURRENT_STATE"
WS_TYPE_SENSOR_STATE: Final = "SENSOR_STATE"
WS_TYPE_FACTOR_CURRENT_STATE: Final = "FACTOR_CURRENT_STATE"
WS_TYPE_FACTOR_TARGET_STATE: Final = "FACTOR_TARGET_STATE"
WS_TYPE_OBJECTIVE_STATE: Final = "OBJECTIVE_STATE"
WS_TYPE_DATA_PROVIDER: Final = "DATA_PROVIDER"
WS_TYPE_ENTITY_MANAGEMENT: Final = "ENTITY_MANAGEMENT"
