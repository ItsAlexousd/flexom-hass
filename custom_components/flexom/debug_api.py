"""Utilities for testing API connectivity for the Flexom integration."""
import aiohttp
import logging
from typing import Dict, Any, List, Optional

from .hemisphere import HemisphereApiClient
from .hemis import HemisApiClient

_LOGGER = logging.getLogger(__name__)

async def test_api_connectivity(username: str, password: str) -> Dict[str, Any]:
    """Test connectivity to all necessary APIs and log results."""
    results = {
        "hemisphere_auth": False,
        "building_info": False,
        "zones": None,
        "actuators": None,
        "errors": []
    }
    
    session = None
    hemisphere_client = None
    hemis_client = None
    
    try:
        _LOGGER.info("Starting API connectivity diagnostic test")
        session = aiohttp.ClientSession()
        
        # Step 1: Test Hemisphere authentication
        _LOGGER.info("Testing Hemisphere authentication with %s", username)
        hemisphere_client = HemisphereApiClient(session)
        auth_success = await hemisphere_client.authenticate(username, password)
        
        if not auth_success:
            error_msg = "Failed to authenticate with Hemisphere API"
            _LOGGER.error(error_msg)
            results["errors"].append(error_msg)
            return results
        
        results["hemisphere_auth"] = True
        _LOGGER.info("✓ Successfully authenticated with Hemisphere")
        _LOGGER.info("Token: %s...", hemisphere_client.hemisphere_token[:10] if hemisphere_client.hemisphere_token else "None")
        
        # Step 2: Check building info
        building_id = hemisphere_client.building_id
        hemis_base_url = hemisphere_client.hemis_base_url
        hemis_stomp_url = hemisphere_client.hemis_stomp_url
        
        if not building_id or not hemis_base_url or not hemis_stomp_url:
            error_msg = "Failed to get Hemis building info"
            _LOGGER.error(error_msg)
            results["errors"].append(error_msg)
            return results
        
        results["building_info"] = True
        _LOGGER.info("✓ Retrieved building information successfully")
        _LOGGER.info("Building ID: %s", building_id)
        _LOGGER.info("Hemis base URL: %s", hemis_base_url)
        _LOGGER.info("Hemis STOMP URL: %s", hemis_stomp_url)
        
        # Step 3: Test Hemis API
        _LOGGER.info("Testing Hemis API connectivity")
        hemis_client = HemisApiClient(
            session,
            hemis_base_url,
            hemisphere_client.hemisphere_token
        )
        
        # Step 3.1: Test zones API
        _LOGGER.info("Fetching zones from Hemis API")
        zones = await hemis_client.get_zones()
        
        if zones is None:
            error_msg = "Failed to fetch zones from Hemis API"
            _LOGGER.error(error_msg)
            results["errors"].append(error_msg)
        else:
            _LOGGER.info("✓ Successfully fetched %d zones", len(zones))
            results["zones"] = len(zones)
            
            # Log zone details
            for zone in zones:
                zone_id = zone.get("id")
                zone_name = zone.get("name")
                _LOGGER.info("Zone: %s - %s", zone_id, zone_name)
                
                # Get zone factors
                _LOGGER.info("Fetching factors for zone %s", zone_id)
                factors = await hemis_client.get_zone_factors(zone_id)
                
                if factors is None:
                    _LOGGER.warning("Failed to fetch factors for zone %s", zone_id)
                else:
                    _LOGGER.info("✓ Found %d factors for zone %s", len(factors), zone_id)
                    for factor in factors:
                        factor_id = factor.get("id")
                        factor_name = factor.get("name")
                        factor_type = factor.get("factorTypeId")
                        _LOGGER.info("  Factor: %s - %s (Type: %s)", factor_id, factor_name, factor_type)
        
        # Step 3.2: Test actuators API
        _LOGGER.info("Fetching actuators from Hemis API")
        actuators = await hemis_client.get_actuators()
        
        if actuators is None:
            error_msg = "Failed to fetch actuators from Hemis API"
            _LOGGER.error(error_msg)
            results["errors"].append(error_msg)
        else:
            _LOGGER.info("✓ Successfully fetched %d actuators", len(actuators))
            results["actuators"] = len(actuators)
            
            # Log actuator details
            for actuator in actuators:
                actuator_id = actuator.get("id")
                actuator_name = actuator.get("name")
                actuator_type = actuator.get("typeName")
                
                # Check if it's a light actuator
                is_light = any(
                    state.get("factorId") == "BRI" 
                    for state in actuator.get("states", [])
                )
                
                if is_light:
                    _LOGGER.info("Light Actuator: %s - %s (Type: %s)", 
                                actuator_id, actuator_name, actuator_type)
                    for state in actuator.get("states", []):
                        factor_id = state.get("factorId")
                        state_value = state.get("value")
                        _LOGGER.info("  State: %s = %s", factor_id, state_value)
                else:
                    _LOGGER.info("Other Actuator: %s - %s (Type: %s)", 
                                actuator_id, actuator_name, actuator_type)
        
        # Step 4: Test WebSocket URL
        _LOGGER.info("Testing WebSocket URL: %s", hemis_stomp_url)
        try:
            import websockets
            import ssl
            
            # Parse the URL
            from urllib.parse import urlparse
            parsed_url = urlparse(hemis_stomp_url)
            scheme = "wss" if parsed_url.scheme == "https" else "ws"
            host = parsed_url.netloc
            
            # Create full WebSocket URL
            ws_url = f"{scheme}://{host}{parsed_url.path}"
            _LOGGER.info("Connecting to WebSocket at: %s", ws_url)
            
            # Only test connection without actually establishing it
            ssl_context = ssl.create_default_context() if scheme == "wss" else None
            async with websockets.connect(
                ws_url, 
                ssl=ssl_context,
                close_timeout=5
            ) as ws:
                _LOGGER.info("✓ Successfully connected to WebSocket")
                # We don't need to do anything else, just checking if connection works
                
        except Exception as ws_err:
            error_msg = f"Failed to connect to WebSocket: {str(ws_err)}"
            _LOGGER.error(error_msg)
            results["errors"].append(error_msg)
        
        return results
        
    except Exception as e:
        error_msg = f"Unexpected error during API diagnostic: {str(e)}"
        _LOGGER.error(error_msg, exc_info=True)
        results["errors"].append(error_msg)
        return results
        
    finally:
        # Clean up resources
        if session:
            await session.close()
        _LOGGER.info("API connectivity test completed")
