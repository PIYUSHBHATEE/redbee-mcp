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
    """Authentifie un utilisateur avec ses identifiants"""
    
    try:
        async with RedBeeClient(config) as client:
            auth_response = await client.authenticate(username, password)
            
            response = {
                "success": True,
                "session_token": auth_response.session_token,
                "device_id": auth_response.device_id,
                "expires_at": auth_response.expires_at.isoformat() if auth_response.expires_at else None,
                "message": "Authentification réussie"
            }
            
            return [TextContent(
                type="text",
                text=f"Authentification Red Bee Media:\n{json.dumps(response, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur d'authentification Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de l'authentification: {str(e)}"
        )]


async def create_anonymous_session(
    config: RedBeeConfig
) -> List[TextContent]:
    """Crée une session anonyme via l'endpoint v2"""
    
    try:
        async with RedBeeClient(config) as client:
            # Utiliser l'endpoint v2 correct selon la documentation
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
                "message": "Session anonyme créée"
            }
            
            return [TextContent(
                type="text",
                text=f"Session anonyme Red Bee Media:\n{json.dumps(response, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur création session anonyme Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la création de session anonyme: {str(e)}"
        )]


async def validate_session_token(
    config: RedBeeConfig,
    session_token: str
) -> List[TextContent]:
    """Valide un token de session via l'endpoint v2"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = session_token
            
            # Utiliser l'endpoint v2 correct selon la documentation
            result = await client._make_request(
                "GET",
                f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/auth/session",
                include_auth=True
            )
            
            response = {
                "valid": True,
                "session_token": session_token,
                "validation_result": result,
                "message": "Token de session valide"
            }
            
            return [TextContent(
                type="text",
                text=f"Validation token Red Bee Media:\n{json.dumps(response, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Token invalide Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la validation: {str(e)}"
        )]


async def logout_user(
    config: RedBeeConfig,
    session_token: str
) -> List[TextContent]:
    """Déconnecte un utilisateur via l'endpoint v2"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = session_token
            
            # Utiliser l'endpoint v2 correct selon la documentation
            await client._make_request(
                "DELETE",
                f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/auth/session/delete",
                include_auth=True
            )
            
            response = {
                "success": True,
                "message": "Déconnexion réussie"
            }
            
            return [TextContent(
                type="text",
                text=f"Déconnexion Red Bee Media:\n{json.dumps(response, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur déconnexion Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la déconnexion: {str(e)}"
        )]


# MCP Tool definitions
AUTH_TOOLS = [
    Tool(
        name="login_user",
        description="Authentifie un utilisateur avec ses identifiants et retourne un token de session",
        inputSchema={
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "Nom d'utilisateur ou email"
                },
                "password": {
                    "type": "string",
                    "description": "Mot de passe de l'utilisateur"
                },
                "remember_me": {
                    "type": "boolean",
                    "description": "Se souvenir de la session (optionnel)",
                    "default": False
                }
            },
            "required": ["username", "password"]
        }
    ),
    Tool(
        name="create_anonymous_session",
        description="Crée une session anonyme pour accéder au contenu public",
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
        description="Valide un token de session existant",
        inputSchema={
            "type": "object",
            "properties": {
                "session_token": {
                    "type": "string",
                    "description": "Token de session à valider"
                }
            },
            "required": ["session_token"]
        }
    ),
    Tool(
        name="logout_user",
        description="Déconnecte un utilisateur et invalide sa session",
        inputSchema={
            "type": "object",
            "properties": {
                "session_token": {
                    "type": "string",
                    "description": "Token de session à invalider"
                }
            },
            "required": ["session_token"]
        }
    )
] 

def get_all_auth_tools() -> List[Tool]:
    """Return all authentication tools"""
    return AUTH_TOOLS 