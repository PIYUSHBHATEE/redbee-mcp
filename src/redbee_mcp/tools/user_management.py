"""
MCP Tools for Red Bee Media User Management

This module provides user management tools for Red Bee Media platform.
"""

import json
from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent

from ..client import RedBeeClient, RedBeeAPIError
from ..models import RedBeeConfig


async def signup_user(
    config: RedBeeConfig,
    username: str,
    password: str,
    email: Optional[str] = None,
    firstName: Optional[str] = None,
    lastName: Optional[str] = None
) -> List[TextContent]:
    """Creates a new user account"""
    
    try:
        async with RedBeeClient(config) as client:
            signup_data = {
                "username": username,
                "password": password
            }
            
            if email:
                signup_data["email"] = email
            if firstName:
                signup_data["firstName"] = firstName
            if lastName:
                signup_data["lastName"] = lastName
            
            result = await client._make_request(
                "POST",
                f"/v3/customer/{config.customer}/businessunit/{config.business_unit}/user/signup",
                data=signup_data,
                include_auth=False
            )
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media User Registration:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee registration error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during registration: {str(e)}"
        )]


async def change_user_password(
    config: RedBeeConfig,
    sessionToken: str,
    oldPassword: str,
    newPassword: str
) -> List[TextContent]:
    """Changes a user's password"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = sessionToken
            
            password_data = {
                "oldPassword": oldPassword,
                "newPassword": newPassword
            }
            
            result = await client._make_request(
                "PUT",
                f"/v3/customer/{config.customer}/businessunit/{config.business_unit}/user/changePassword",
                data=password_data,
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media Password Change:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee password change error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during password change: {str(e)}"
        )]


async def get_user_profiles(
    config: RedBeeConfig,
    sessionToken: str
) -> List[TextContent]:
    """Retrieves all profiles for a user"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = sessionToken
            
            result = await client._make_request(
                "GET",
                f"/v3/customer/{config.customer}/businessunit/{config.business_unit}/user/profiles",
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media User Profiles:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee profiles retrieval error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during profiles retrieval: {str(e)}"
        )]


async def add_user_profile(
    config: RedBeeConfig,
    sessionToken: str,
    profileName: str,
    dateOfBirth: Optional[str] = None,
    avatar: Optional[str] = None
) -> List[TextContent]:
    """Adds a new user profile"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = sessionToken
            
            profile_data = {
                "profileName": profileName
            }
            
            if dateOfBirth:
                profile_data["dateOfBirth"] = dateOfBirth
            if avatar:
                profile_data["avatar"] = avatar
            
            result = await client._make_request(
                "POST",
                f"/v3/customer/{config.customer}/businessunit/{config.business_unit}/user/profiles",
                data=profile_data,
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media New User Profile:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee profile creation error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during profile creation: {str(e)}"
        )]


async def select_user_profile(
    config: RedBeeConfig,
    sessionToken: str,
    profileId: str
) -> List[TextContent]:
    """Selects an active user profile"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = sessionToken
            
            result = await client._make_request(
                "PUT",
                f"/v3/customer/{config.customer}/businessunit/{config.business_unit}/user/profiles/{profileId}/select",
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media User Profile Selection:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee profile selection error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during profile selection: {str(e)}"
        )]


async def get_user_preferences(
    config: RedBeeConfig,
    sessionToken: str
) -> List[TextContent]:
    """Retrieves user preferences"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = sessionToken
            
            result = await client._make_request(
                "GET",
                f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/user/preferences",
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media User Preferences:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee preferences retrieval error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during preferences retrieval: {str(e)}"
        )]


async def set_user_preferences(
    config: RedBeeConfig,
    sessionToken: str,
    preferences: Dict[str, Any]
) -> List[TextContent]:
    """Sets user preferences"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = sessionToken
            
            result = await client._make_request(
                "PUT",
                f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/user/preferences",
                data=preferences,
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media Preferences Update:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee preferences update error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during preferences update: {str(e)}"
        )]


# MCP Tool definitions
USER_MANAGEMENT_TOOLS = [
    Tool(
        name="signup_user",
        description="Creates a new user account",
        inputSchema={
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "Username"
                },
                "password": {
                    "type": "string",
                    "description": "Password"
                },
                "email": {
                    "type": "string",
                    "description": "Email address (optional)"
                },
                "firstName": {
                    "type": "string",
                    "description": "First name (optional)"
                },
                "lastName": {
                    "type": "string",
                    "description": "Last name (optional)"
                }
            },
            "required": ["username", "password"]
        }
    ),
    Tool(
        name="change_user_password",
        description="Changes a user's password",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "User session token"
                },
                "oldPassword": {
                    "type": "string",
                    "description": "Old password"
                },
                "newPassword": {
                    "type": "string",
                    "description": "New password"
                }
            },
            "required": ["sessionToken", "oldPassword", "newPassword"]
        }
    ),
    Tool(
        name="get_user_profiles",
        description="Retrieves all profiles for a user",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "User session token"
                }
            },
            "required": ["sessionToken"]
        }
    ),
    Tool(
        name="add_user_profile",
        description="Adds a new user profile",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "User session token"
                },
                "profileName": {
                    "type": "string",
                    "description": "Profile name"
                },
                "dateOfBirth": {
                    "type": "string",
                    "description": "Date of birth (optional)"
                },
                "avatar": {
                    "type": "string",
                    "description": "Avatar URL (optional)"
                }
            },
            "required": ["sessionToken", "profileName"]
        }
    ),
    Tool(
        name="select_user_profile",
        description="Selects an active user profile",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "User session token"
                },
                "profileId": {
                    "type": "string",
                    "description": "Profile ID to select"
                }
            },
            "required": ["sessionToken", "profileId"]
        }
    ),
    Tool(
        name="get_user_preferences",
        description="Retrieves user preferences",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "User session token"
                }
            },
            "required": ["sessionToken"]
        }
    ),
    Tool(
        name="set_user_preferences",
        description="Sets user preferences",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "User session token"
                },
                "preferences": {
                    "type": "object",
                    "description": "Object containing preferences to set"
                }
            },
            "required": ["sessionToken", "preferences"]
        }
    )
] 

def get_all_user_management_tools() -> List[Tool]:
    """Return all user management tools"""
    return USER_MANAGEMENT_TOOLS 