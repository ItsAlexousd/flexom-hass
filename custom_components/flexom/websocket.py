"""WebSocket client for Hemis."""
import asyncio
import json
import logging
import urllib.parse
from typing import Any, Callable, Dict, Optional, List

import stomper
import websockets
from homeassistant.core import HomeAssistant

from .const import STOMP_TOPIC_DATA

_LOGGER = logging.getLogger(__name__)

FACTOR_TYPES = ["BRI", "BRIEXT", "TMP"]
EVENT_TYPES = [
    "ACTUATOR_TARGET_STATE",
    "ACTUATOR_HARDWARE_STATE",
    "ACTUATOR_CURRENT_STATE",
    "SENSOR_STATE",
    "IT_STATE",
    "FACTOR_TARGET_STATE",
    "FACTOR_CURRENT_STATE",
    "OBJECTIVE_STATE",
    "DATA_PROVIDER",
    "ENTITY_MANAGEMENT"
]

class HemisWebSocketClient:
    """WebSocket client for Hemis."""

    def __init__(
        self, 
        hass: HomeAssistant,
        stomp_url: str,
        building_id: str,
        token: str,
        message_callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """Initialize the WebSocket client."""
        self.hass = hass
        self.stomp_url = stomp_url
        self.building_id = building_id
        self.token = token
        self.message_callback = message_callback
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.task: Optional[asyncio.Task] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.is_running = False
        self.subscription_id = "1"
        self.connection_id = None

    async def connect(self) -> bool:
        """Connect to the WebSocket server."""
        try:
            # Parse the URL
            parsed_url = urllib.parse.urlparse(self.stomp_url)
            _LOGGER.debug("Connecting to WebSocket URL: %s", self.stomp_url)
            
            # Use WebSocketApp from websockets library
            self.ws = await websockets.connect(
                self.stomp_url,
                ssl=parsed_url.scheme == "wss"
            )
            
            _LOGGER.debug("WebSocket connection established")
            
            # Send STOMP CONNECT frame
            connect_frame = stomper.Frame()
            connect_frame.cmd = "CONNECT"
            connect_frame.headers = {
                "accept-version": "1.0,1.1,1.2",
                "host": parsed_url.netloc,
                "login": self.building_id,
                "passcode": self.token,
                "heart-beat": "20000,20000"
            }
            
            connect_str = connect_frame.pack()
            _LOGGER.debug("Sending STOMP CONNECT frame: %s", connect_str)
            await self.ws.send(connect_str)
            
            # Wait for CONNECTED response
            response = await self.ws.recv()
            _LOGGER.debug("Received from WebSocket: %s", response)
            
            # Convert bytes to string if necessary
            if isinstance(response, bytes):
                response_str = response.decode('utf-8')
            else:
                response_str = response
            
            if not response_str.startswith("CONNECTED"):
                _LOGGER.error("Failed to connect to Hemis WebSocket: %s", response_str)
                return False
                
            # Extract connection ID from response
            for line in response_str.splitlines():
                if line.startswith("session:"):
                    self.connection_id = line.split(":")[1].strip()
                    _LOGGER.debug("Got session ID: %s", self.connection_id)
            
            # Subscribe to the data topic
            topic = STOMP_TOPIC_DATA.format(building_id=self.building_id)
            _LOGGER.debug("Subscribing to topic: %s", topic)
            
            subscribe_frame = stomper.Frame()
            subscribe_frame.cmd = "SUBSCRIBE"
            subscribe_frame.headers = {
                "id": self.subscription_id,
                "destination": topic,
                "ack": "auto"
            }
            
            subscribe_str = subscribe_frame.pack()
            await self.ws.send(subscribe_str)
            
            # Start heartbeat task
            if self.heartbeat_task is None:
                self.heartbeat_task = asyncio.create_task(self._send_heartbeats())
            
            _LOGGER.info("Connected to Hemis WebSocket and subscribed to topics")
            return True
            
        except Exception as err:
            _LOGGER.error("Error connecting to Hemis WebSocket: %s", err)
            return False

    async def disconnect(self) -> None:
        """Disconnect from the WebSocket server."""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
            self.heartbeat_task = None
            
        if self.task:
            self.is_running = False
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None
        
        if self.ws:
            # Send STOMP DISCONNECT frame
            disconnect_frame = stomper.Frame()
            disconnect_frame.cmd = "DISCONNECT"
            if self.connection_id:
                disconnect_frame.headers = {"receipt": self.connection_id}
            
            try:
                await self.ws.send(disconnect_frame.pack())
                await self.ws.close()
                _LOGGER.info("Disconnected from Hemis WebSocket")
            except Exception as err:
                _LOGGER.error("Error disconnecting from Hemis WebSocket: %s", err)
            finally:
                self.ws = None

    async def start_listening(self) -> None:
        """Start listening for messages."""
        if self.task:
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._listen())

    async def _listen(self) -> None:
        """Listen for messages."""
        if not self.ws:
            _LOGGER.error("WebSocket not connected")
            return
            
        try:
            while self.is_running:
                message = await self.ws.recv()
                
                if not message:
                    continue
                
                # Convert bytes to string if necessary
                if isinstance(message, bytes):
                    message_str = message.decode('utf-8')
                else:
                    message_str = message
                    
                _LOGGER.debug("Received WebSocket message: %s", message_str[:100])
                
                if message_str.startswith("MESSAGE"):
                    # Extract message body using a manual split approach
                    try:
                        # Split into headers and body - the body comes after a blank line
                        parts = message_str.split("\n\n", 1)
                        if len(parts) < 2:
                            continue
                            
                        body = parts[1].rstrip('\x00')
                        try:
                            # Nettoyage du corps JSON
                            if "}" in body:
                                # Trouver la fin du premier objet JSON (le contenu valide)
                                json_end = body.find("}") + 1
                                if json_end > 0:
                                    cleaned_body = body[:json_end]
                                    data = json.loads(cleaned_body)
                                    _LOGGER.debug("Successfully parsed message: %s", data)
                                    
                                    # Ne traiter que les types d'événements connus
                                    if "type" in data and data["type"] in EVENT_TYPES:
                                        # Appel direct au callback sans créer de tâche
                                        self.message_callback(data)
                                    else:
                                        _LOGGER.debug("Ignoring unknown event type: %s", data.get("type"))
                                else:
                                    _LOGGER.warning("Could not find JSON end marker in body")
                            else:
                                _LOGGER.warning("No JSON object found in message body")
                        except json.JSONDecodeError as e:
                            _LOGGER.error("Invalid JSON received: %s - Error: %s", body, str(e))
                    except Exception as e:
                        _LOGGER.error("Error processing message: %s - Error: %s", message_str[:100], str(e))
                
                elif message_str.startswith("ERROR"):
                    _LOGGER.error("STOMP error: %s", message_str)
                    self.is_running = False
                    break
                    
                # Réinitialiser la connexion si nécessaire
                elif message_str.startswith("RECEIPT"):
                    _LOGGER.debug("Received RECEIPT frame: %s", message_str)
                
        except websockets.ConnectionClosed:
            _LOGGER.warning("WebSocket connection closed, attempting reconnect in 5 seconds")
            await asyncio.sleep(5)
            # Tenter de se reconnecter
            if await self.connect():
                self.is_running = True
                self.task = asyncio.create_task(self._listen())
        except Exception as err:
            _LOGGER.error("Error in WebSocket listener: %s", err)
        finally:
            self.is_running = False
            
    async def _send_heartbeats(self) -> None:
        """Send heartbeats to keep the connection alive."""
        try:
            while True:
                await asyncio.sleep(15)  # Send heartbeat every 15 seconds
                if self.ws and not self.ws.closed:
                    try:
                        await self.ws.send("\n")
                        _LOGGER.debug("Sent heartbeat")
                    except Exception as err:
                        _LOGGER.error("Error sending heartbeat: %s", err)
                        break
        except asyncio.CancelledError:
            _LOGGER.debug("Heartbeat task cancelled")
        except Exception as err:
            _LOGGER.error("Error in heartbeat task: %s", err)
            
    def update_token(self, new_token: str) -> None:
        """Update the authentication token."""
        self.token = new_token
        _LOGGER.debug("Updated WebSocket token")
