"""
MCP Tools for Red Bee Media Authentication

This module provides authentication-related tools for Red Bee Media platform.
"""

import json
import base64
from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent

from ..client import RedBeeClient, RedBeeAPIError
from ..models import RedBeeConfig


async def login_user(
    config: RedBeeConfig,
    username: str,
    password: str,
    remember_me: Optional[bool] = False
) -> List[TextContent]:
    """Authenticates a user with their credentials"""
    
    try:
        async with RedBeeClient(config) as client:
            auth_response = await client.authenticate(username, password)
            
            response = {
                "success": True,
                "session_token": auth_response.session_token,
                "device_id": auth_response.device_id,
                "expires_at": auth_response.expires_at.isoformat() if auth_response.expires_at else None,
                "message": "Authentication successful"
            }
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media Authentication:\n{json.dumps(response, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee authentication error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during authentication: {str(e)}"
        )]


async def create_anonymous_session(
    config: RedBeeConfig
) -> List[TextContent]:
    """Creates an anonymous session via v2 endpoint"""
    
    try:
        async with RedBeeClient(config) as client:
            # Use the correct v2 endpoint according to documentation
            result = await client._make_request(
                "POST",
                f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/auth/anonymous",
                data={
                    "device": {
                        "deviceId": config.device_id or client.device_id,
                        "type": "WEB"
                    }
                },
                include_auth=False
            )
            
            response = {
                "success": True,
                "session_token": result.get("sessionToken"),
                "device_id": result.get("deviceId"),
                "expires_at": result.get("expiresAt"),
                "session_type": "anonymous",
                "message": "Anonymous session created"
            }
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media Anonymous Session:\n{json.dumps(response, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee anonymous session creation error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during anonymous session creation: {str(e)}"
        )]


async def validate_session_token(
    config: RedBeeConfig,
    session_token: str
) -> List[TextContent]:
    """Validates a session token via v2 endpoint"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = session_token
            
            # Use the correct v2 endpoint according to documentation
            result = await client._make_request(
                "GET",
                f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/auth/session",
                include_auth=True
            )
            
            response = {
                "valid": True,
                "session_token": session_token,
                "validation_result": result,
                "message": "Session token is valid"
            }
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media Token Validation:\n{json.dumps(response, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee invalid token: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during validation: {str(e)}"
        )]


async def logout_user(
    config: RedBeeConfig,
    session_token: str
) -> List[TextContent]:
    """Logs out a user via v2 endpoint"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = session_token
            
            # Use the correct v2 endpoint according to documentation
            await client._make_request(
                "DELETE",
                f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/auth/session/delete",
                include_auth=True
            )
            
            response = {
                "success": True,
                "message": "Logout successful"
            }
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media Logout:\n{json.dumps(response, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee logout error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during logout: {str(e)}"
        )]


# MCP Tool definitions
AUTH_TOOLS = [
    Tool(
        name="login_user",
        description="Authenticates a user with their credentials and returns a session token",
        inputSchema={
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "Username or email"
                },
                "password": {
                    "type": "string",
                    "description": "User password"
                },
                "remember_me": {
                    "type": "boolean",
                    "description": "Remember the session (optional)",
                    "default": False
                }
            },
            "required": ["username", "password"]
        }
    ),
    Tool(
        name="create_anonymous_session",
        description="Creates an anonymous session to access public content",
        inputSchema={
            "type": "object",
            "properties": {
                "random_string": {
                    "type": "string",
                    "description": "Dummy parameter for no-parameter tools"
                }
            },
            "required": ["random_string"]
        }
    ),
    Tool(
        name="validate_session_token",
        description="Validates an existing session token",
        inputSchema={
            "type": "object",
            "properties": {
                "session_token": {
                    "type": "string",
                    "description": "Session token to validate"
                }
            },
            "required": ["session_token"]
        }
    ),
    Tool(
        name="logout_user",
        description="Logs out a user and invalidates their session",
        inputSchema={
            "type": "object",
            "properties": {
                "session_token": {
                    "type": "string",
                    "description": "Session token to invalidate"
                }
            },
            "required": ["session_token"]
        }
    )
] 

def get_all_auth_tools() -> List[Tool]:
    """Return all authentication tools"""
    return AUTH_TOOLS 