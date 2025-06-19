"""
MCP Tools for Red Bee Media System Information

This module provides system information tools for Red Bee Media platform.
"""

import json
from typing import List
from mcp.types import TextContent, Tool

async def get_system_config_impl(config, session_token=None):
    """Get system configuration via v2 endpoint"""
    import httpx
    
    try:
        url = f"{config.exposure_base_url}/v2/customer/{config.customer}/businessunit/{config.business_unit}/session/config"
        headers = {
            "accept": "application/json"
        }
        if session_token:
            headers["authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            result = response.json()
            
            return [
                TextContent(
                    type="text",
                    text=f"Red Bee Media System Configuration:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
                )
            ]
    except Exception as e:
        return [
            TextContent(
                type="text", 
                text=f"Error getting system configuration: {str(e)}"
            )
        ]

async def get_system_time_impl(config, session_token=None):
    """Get system time via v1 endpoint"""
    import httpx
    
    try:
        url = f"{config.exposure_base_url}/v1/time"
        headers = {
            "accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            result = response.json()
            
            return [
                TextContent(
                    type="text",
                    text=f"Red Bee Media System Time:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
                )
            ]
    except Exception as e:
        return [
            TextContent(
                type="text", 
                text=f"Error getting system time: {str(e)}"
            )
        ]

async def get_user_location_impl(config, session_token=None):
    """Get user location information"""
    import httpx
    
    try:
        url = f"{config.exposure_base_url}/v1/customer/{config.customer}/businessunit/{config.business_unit}/geoip"
        headers = {
            "accept": "application/json"
        }
        if session_token:
            headers["authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            result = response.json()
            
            return [
                TextContent(
                    type="text",
                    text=f"User Location Information:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
                )
            ]
    except Exception as e:
        return [
            TextContent(
                type="text", 
                text=f"Error getting location: {str(e)}"
            )
        ]

async def get_active_channels_impl(config, session_token=None):
    """Get active channels"""
    import httpx
    
    try:
        url = f"{config.exposure_base_url}/v1/customer/{config.customer}/businessunit/{config.business_unit}/content/asset"
        headers = {
            "accept": "application/json"
        }
        if session_token:
            headers["authorization"] = f"Bearer {session_token}"
        
        params = {
            "assetType": "CHANNEL",
            "pageSize": 50
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            result = response.json()
            
            return [
                TextContent(
                    type="text",
                    text=f"Active Channels:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
                )
            ]
    except Exception as e:
        return [
            TextContent(
                type="text", 
                text=f"Error getting channels: {str(e)}"
            )
        ]

async def get_user_devices_impl(config, session_token=None):
    """Get user devices"""
    import httpx
    
    try:
        url = f"{config.exposure_base_url}/v1/customer/{config.customer}/businessunit/{config.business_unit}/user/device"
        headers = {
            "accept": "application/json"
        }
        if session_token:
            headers["authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            result = response.json()
            
            return [
                TextContent(
                    type="text",
                    text=f"User Devices:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
                )
            ]
    except Exception as e:
        return [
            TextContent(
                type="text", 
                text=f"Error getting devices: {str(e)}"
            )
        ]

async def delete_user_device_impl(config, device_id, session_token=None):
    """Delete a user device"""
    import httpx
    
    try:
        url = f"{config.exposure_base_url}/v1/customer/{config.customer}/businessunit/{config.business_unit}/user/device/{device_id}"
        headers = {
            "accept": "application/json"
        }
        if session_token:
            headers["authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers)
            
            if response.status_code == 204:
                return [
                    TextContent(
                        type="text",
                        text=f"Device {device_id} successfully deleted"
                    )
                ]
            else:
                result = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                return [
                    TextContent(
                        type="text",
                        text=f"Delete device response ({response.status_code}):\n{json.dumps(result, indent=2) if isinstance(result, dict) else result}"
                    )
                ]
    except Exception as e:
        return [
            TextContent(
                type="text", 
                text=f"Error deleting device: {str(e)}"
            )
        ]

# MCP Tool definitions
SYSTEM_TOOLS = [
    Tool(
        name="get_system_config",
        description="Get Red Bee Media platform system configuration",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="get_system_time",
        description="Get Red Bee Media server system time",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="get_user_location",
        description="Get user geographical location based on IP",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="get_active_channels",
        description="Get list of active channels on the platform",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="get_user_devices",
        description="Get list of user registered devices",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="delete_user_device",
        description="Delete a user device by device ID",
        inputSchema={
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "Device ID to delete"
                }
            },
            "required": ["device_id"]
        }
    )
]

def get_all_system_tools() -> List[Tool]:
    """Return all system tools"""
    return SYSTEM_TOOLS 