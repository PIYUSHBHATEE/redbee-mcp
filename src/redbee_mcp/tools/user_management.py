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
    """Crée un nouveau compte utilisateur"""
    
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
                text=f"Inscription utilisateur Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur inscription Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de l'inscription: {str(e)}"
        )]


async def change_user_password(
    config: RedBeeConfig,
    sessionToken: str,
    oldPassword: str,
    newPassword: str
) -> List[TextContent]:
    """Change le mot de passe d'un utilisateur"""
    
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
                text=f"Changement de mot de passe Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur changement mot de passe Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors du changement de mot de passe: {str(e)}"
        )]


async def get_user_profiles(
    config: RedBeeConfig,
    sessionToken: str
) -> List[TextContent]:
    """Récupère tous les profils d'un utilisateur"""
    
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
                text=f"Profils utilisateur Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur récupération profils Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la récupération des profils: {str(e)}"
        )]


async def add_user_profile(
    config: RedBeeConfig,
    sessionToken: str,
    profileName: str,
    dateOfBirth: Optional[str] = None,
    avatar: Optional[str] = None
) -> List[TextContent]:
    """Ajoute un nouveau profil utilisateur"""
    
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
                text=f"Nouveau profil utilisateur Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur création profil Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la création du profil: {str(e)}"
        )]


async def select_user_profile(
    config: RedBeeConfig,
    sessionToken: str,
    profileId: str
) -> List[TextContent]:
    """Sélectionne un profil utilisateur actif"""
    
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
                text=f"Sélection profil utilisateur Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur sélection profil Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la sélection du profil: {str(e)}"
        )]


async def get_user_preferences(
    config: RedBeeConfig,
    sessionToken: str
) -> List[TextContent]:
    """Récupère les préférences utilisateur"""
    
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
                text=f"Préférences utilisateur Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur récupération préférences Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la récupération des préférences: {str(e)}"
        )]


async def set_user_preferences(
    config: RedBeeConfig,
    sessionToken: str,
    preferences: Dict[str, Any]
) -> List[TextContent]:
    """Définit les préférences utilisateur"""
    
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
                text=f"Mise à jour préférences Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur mise à jour préférences Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la mise à jour des préférences: {str(e)}"
        )]


# MCP Tool definitions
USER_MANAGEMENT_TOOLS = [
    Tool(
        name="signup_user",
        description="Crée un nouveau compte utilisateur",
        inputSchema={
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "Nom d'utilisateur"
                },
                "password": {
                    "type": "string",
                    "description": "Mot de passe"
                },
                "email": {
                    "type": "string",
                    "description": "Adresse email (optionnel)"
                },
                "firstName": {
                    "type": "string",
                    "description": "Prénom (optionnel)"
                },
                "lastName": {
                    "type": "string",
                    "description": "Nom de famille (optionnel)"
                }
            },
            "required": ["username", "password"]
        }
    ),
    Tool(
        name="change_user_password",
        description="Change le mot de passe d'un utilisateur",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "Token de session utilisateur"
                },
                "oldPassword": {
                    "type": "string",
                    "description": "Ancien mot de passe"
                },
                "newPassword": {
                    "type": "string",
                    "description": "Nouveau mot de passe"
                }
            },
            "required": ["sessionToken", "oldPassword", "newPassword"]
        }
    ),
    Tool(
        name="get_user_profiles",
        description="Récupère tous les profils d'un utilisateur",
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
        name="add_user_profile",
        description="Ajoute un nouveau profil utilisateur",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "Token de session utilisateur"
                },
                "profileName": {
                    "type": "string",
                    "description": "Nom du profil"
                },
                "dateOfBirth": {
                    "type": "string",
                    "description": "Date de naissance (optionnel)"
                },
                "avatar": {
                    "type": "string",
                    "description": "URL de l'avatar (optionnel)"
                }
            },
            "required": ["sessionToken", "profileName"]
        }
    ),
    Tool(
        name="select_user_profile",
        description="Sélectionne un profil utilisateur actif",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "Token de session utilisateur"
                },
                "profileId": {
                    "type": "string",
                    "description": "ID du profil à sélectionner"
                }
            },
            "required": ["sessionToken", "profileId"]
        }
    ),
    Tool(
        name="get_user_preferences",
        description="Récupère les préférences utilisateur",
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
        name="set_user_preferences",
        description="Définit les préférences utilisateur",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "Token de session utilisateur"
                },
                "preferences": {
                    "type": "object",
                    "description": "Objet contenant les préférences à définir"
                }
            },
            "required": ["sessionToken", "preferences"]
        }
    )
] 

def get_all_user_management_tools() -> List[Tool]:
    """Return all user management tools"""
    return USER_MANAGEMENT_TOOLS 