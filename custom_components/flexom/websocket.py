"""WebSocket client for Hemis."""
import asyncio
import json
import logging
from typing import Any, Callable, Dict, Optional

import stomper
import websockets
from homeassistant.core import HomeAssistant

from .const import STOMP_TOPIC_DATA

_LOGGER = logging.getLogger(__name__)

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
        self.is_running = False
        self.subscription_id = "1"
        self.connection_id = None

    async def connect(self) -> bool:
        """Connect to the WebSocket server."""
        try:
            self.ws = await websockets.connect(self.stomp_url)
            
            # Send STOMP CONNECT frame
            connect_frame = stomper.connect()
            connect_frame = stomper.Frame()
            connect_frame.cmd = "CONNECT"
            connect_frame.headers = {
                "accept-version": "1.0,1.1,1.2",
                "host": self.stomp_url,
                "login": self.building_id,
                "passcode": self.token,
            }
            await self.ws.send(connect_frame.pack())
            
            # Wait for CONNECTED response
            response = await self.ws.recv()
            
            if not response.startswith("CONNECTED"):
                _LOGGER.error("Failed to connect to Hemis WebSocket: %s", response)
                return False
                
            # Extract connection ID from response
            for line in response.splitlines():
                if line.startswith("session:"):
                    self.connection_id = line.split(":")[1].strip()
            
            # Subscribe to the data topic
            topic = STOMP_TOPIC_DATA.format(building_id=self.building_id)
            subscribe_frame = stomper.subscribe(topic, self.subscription_id, ack="auto")
            await self.ws.send(subscribe_frame)
            
            _LOGGER.info("Connected to Hemis WebSocket")
            return True
            
        except Exception as err:
            _LOGGER.error("Error connecting to Hemis WebSocket: %s", err)
            return False

    async def disconnect(self) -> None:
        """Disconnect from the WebSocket server."""
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
            disconnect_frame = stomper.disconnect()
            try:
                await self.ws.send(disconnect_frame)
                await self.ws.close()
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
                
                if message.startswith("MESSAGE"):
                    # Extract message body
                    parts = message.split("\n\n", 1)
                    if len(parts) < 2:
                        continue
                    
                    body = parts[1].rstrip('\x00')
                    try:
                        data = json.loads(body)
                        self.hass.async_create_task(self.message_callback(data))
                    except json.JSONDecodeError:
                        _LOGGER.error("Invalid JSON received: %s", body)
                
                elif message.startswith("ERROR"):
                    _LOGGER.error("STOMP error: %s", message)
                    self.is_running = False
                    break
        except websockets.ConnectionClosed:
            _LOGGER.error("WebSocket connection closed")
        except Exception as err:
            _LOGGER.error("Error in WebSocket listener: %s", err)
        finally:
            self.is_running = False
            
    async def send_heartbeat(self) -> None:
        """Send a heartbeat to keep the connection alive."""
        if self.ws and self.ws.open:
            await self.ws.send("\n")
