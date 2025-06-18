"""
Outils MCP pour les informations système Red Bee Media
Basé sur l'API Exposure de Red Bee Media - Documentation Swagger
"""

import json
from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent

from ..client import RedBeeClient, RedBeeAPIError
from ..models import RedBeeConfig


async def get_system_config(
    config: RedBeeConfig
) -> List[TextContent]:
    """Récupère la configuration système via l'endpoint v2"""
    
    try:
        async with RedBeeClient(config) as client:
            # Utiliser l'endpoint v2 selon la documentation
            result = await client._make_request(
                "GET",
                f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/system/config",
                include_auth=False
            )
            
            return [TextContent(
                type="text",
                text=f"Configuration système Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur API Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la récupération de la config: {str(e)}"
        )]


async def get_system_time(
    config: RedBeeConfig
) -> List[TextContent]:
    """Récupère l'heure système via l'endpoint v1"""
    
    try:
        async with RedBeeClient(config) as client:
            # Utiliser l'endpoint v1 selon la documentation
            result = await client._make_request(
                "GET",
                f"/v1/customer/{config.customer}/businessunit/{config.business_unit}/time",
                include_auth=False
            )
            
            return [TextContent(
                type="text",
                text=f"Heure système Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur API Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la récupération de l'heure: {str(e)}"
        )]


async def get_user_location(
    config: RedBeeConfig
) -> List[TextContent]:
    """Récupère la localisation géographique via l'endpoint v1"""
    
    try:
        async with RedBeeClient(config) as client:
            # Utiliser l'endpoint v1 selon la documentation
            result = await client._make_request(
                "GET",
                f"/v1/customer/{config.customer}/businessunit/{config.business_unit}/location",
                include_auth=False
            )
            
            return [TextContent(
                type="text",
                text=f"Localisation utilisateur Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur API Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la récupération de la localisation: {str(e)}"
        )]


async def get_active_channels(
    config: RedBeeConfig,
    sessionToken: Optional[str] = None
) -> List[TextContent]:
    """Récupère la liste des chaînes actives via l'endpoint channels"""
    
    try:
        async with RedBeeClient(config) as client:
            if sessionToken:
                client.session_token = sessionToken
            elif not client.session_token:
                await client.authenticate_anonymous()
            
            # Utiliser l'endpoint channels selon la documentation
            result = await client._make_request(
                "GET",
                f"/v1/customer/{config.customer}/businessunit/{config.business_unit}/channels",
                include_auth=bool(sessionToken or client.session_token)
            )
            
            return [TextContent(
                type="text",
                text=f"Chaînes actives Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur API Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la récupération des chaînes: {str(e)}"
        )]


async def get_user_devices(
    config: RedBeeConfig,
    sessionToken: str
) -> List[TextContent]:
    """Récupère la liste des appareils via l'endpoint v2 device"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = sessionToken
            
            # Utiliser l'endpoint v2 device selon la documentation
            result = await client._make_request(
                "GET",
                f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/device",
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"Appareils utilisateur Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur API Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la récupération des appareils: {str(e)}"
        )]


async def delete_user_device(
    config: RedBeeConfig,
    sessionToken: str,
    deviceId: str
) -> List[TextContent]:
    """Supprime un appareil via l'endpoint v2 device/{deviceId}"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = sessionToken
            
            # Utiliser l'endpoint v2 device selon la documentation
            result = await client._make_request(
                "DELETE",
                f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/device/{deviceId}",
                include_auth=True
            )
            
            response = {
                "success": True,
                "device_id": deviceId,
                "message": "Appareil supprimé"
            }
            
            return [TextContent(
                type="text",
                text=f"Suppression appareil Red Bee Media:\n{json.dumps(response, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur API Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la suppression de l'appareil: {str(e)}"
        )]


# Définition des outils MCP
SYSTEM_TOOLS = [
    Tool(
        name="get_system_config",
        description="Récupère la configuration système de la plateforme",
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
        name="get_system_time",
        description="Récupère l'heure système du serveur",
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
        name="get_user_location",
        description="Récupère la localisation géographique basée sur l'IP",
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
        name="get_active_channels",
        description="Récupère la liste des chaînes actives",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "Token de session utilisateur (optionnel)"
                }
            },
            "required": []
        }
    ),
    Tool(
        name="get_user_devices",
        description="Récupère la liste des appareils d'un utilisateur",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "Token de session utilisateur"
                }
            },
            "required": ["sessionToken"]
        }
    ),
    Tool(
        name="delete_user_device",
        description="Supprime un appareil de la liste d'un utilisateur",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "Token de session utilisateur"
                },
                "deviceId": {
                    "type": "string",
                    "description": "ID de l'appareil à supprimer"
                }
            },
            "required": ["sessionToken", "deviceId"]
        }
    )
] 