"""
MCP Tools for Red Bee Media Content Management

This module provides content-related tools for Red Bee Media platform.
"""

import json
from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent

from ..client import RedBeeClient, RedBeeAPIError
from ..models import RedBeeConfig


async def get_public_asset_details(
    customer: str,
    business_unit: str,
    assetId: str,
    onlyPublished: Optional[bool] = True,
    fieldSet: Optional[str] = "ALL"
) -> List[TextContent]:
    """Récupère les détails d'un asset via l'endpoint public (sans authentification)"""
    
    try:
        import aiohttp
        
        url = f"https://exposure.api.redbee.live/v1/customer/{customer}/businessunit/{business_unit}/content/asset/{assetId}"
        params = {
            "onlyPublished": str(onlyPublished).lower(),
            "fieldSet": fieldSet
        }
        
        headers = {
            "accept": "application/json;charset=UTF-8"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return [TextContent(
                        type="text",
                        text=f"Détails de l'asset Red Bee Media (Public):\n{json.dumps(result, indent=2, ensure_ascii=False)}"
                    )]
                else:
                    error_text = await response.text()
                    return [TextContent(
                        type="text",
                        text=f"Erreur API Red Bee (Status {response.status}): {error_text}"
                    )]
                    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la récupération: {str(e)}"
        )]


async def search_content(
    config: RedBeeConfig,
    query: Optional[str] = None,
    pageSize: Optional[int] = 50,
    pageNumber: Optional[int] = 1,
    sort: Optional[str] = None,
    includeUserData: Optional[bool] = True
) -> List[TextContent]:
    """Recherche du contenu via l'endpoint v3 searchV3 (SANS authentification)"""
    
    try:
        import aiohttp
        
        # Utiliser l'endpoint v3 public selon la documentation
        if query:
            url = f"https://exposure.api.redbee.live/v3/customer/TV5MONDE/businessunit/TV5MONDEplus/content/search/query/{query}"
        else:
            url = f"https://exposure.api.redbee.live/v3/customer/TV5MONDE/businessunit/TV5MONDEplus/content/search/query/*"
        
        params = {
            "pageSize": pageSize,
            "onlyPublished": "true",
            "fieldSet": "ALL"
        }
        
        if sort:
            params["sort"] = sort
            
        headers = {
            "accept": "application/json;charset=UTF-8"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return [TextContent(
                        type="text",
                        text=f"Résultats de recherche Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
                    )]
                else:
                    error_text = await response.text()
                    return [TextContent(
                        type="text",
                        text=f"Erreur API Red Bee (Status {response.status}): {error_text}"
                    )]
            
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la recherche: {str(e)}"
        )]


async def get_asset_details(
    config: RedBeeConfig,
    assetId: str,
    includeUserData: Optional[bool] = True
) -> List[TextContent]:
    """Récupère les détails complets d'un asset via l'endpoint v1"""
    
    try:
        async with RedBeeClient(config) as client:
            if not client.session_token:
                await client.authenticate_anonymous()
            
            params = {
                "onlyPublished": True,
                "fieldSet": "ALL"
            }
            
            result = await client._make_request(
                "GET",
                f"/v1/customer/{config.customer}/businessunit/{config.business_unit}/content/asset/{assetId}",
                params=params,
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"Détails de l'asset Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur API Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la récupération: {str(e)}"
        )]


async def get_playback_info(
    config: RedBeeConfig,
    assetId: str,
    sessionToken: str
) -> List[TextContent]:
    """Récupère les informations de lecture via l'endpoint v2 play"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = sessionToken
            
            # Utiliser l'endpoint v2 play selon la documentation
            result = await client._make_request(
                "POST",
                f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/entitlement/{assetId}/play",
                data={},
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"Informations de lecture Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur API Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la récupération des infos de lecture: {str(e)}"
        )]


async def search_assets_autocomplete(
    config: RedBeeConfig,
    query: str,
    fieldSet: Optional[str] = "ALL"
) -> List[TextContent]:
    """Autocomplétion de recherche d'assets via l'endpoint v3 (SANS authentification)"""
    
    try:
        import aiohttp
        
        # Utiliser l'endpoint v3 public selon la documentation
        url = f"https://exposure.api.redbee.live/v3/customer/TV5MONDE/businessunit/TV5MONDEplus/content/search/asset/title/autocomplete/{query}"
        
        params = {
            "locales": ["fr"],
            "types": "MOVIE,TV_SHOW"
        }
        
        headers = {
            "accept": "application/json;charset=UTF-8"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return [TextContent(
                        type="text",
                        text=f"Autocomplétion assets Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
                    )]
                else:
                    error_text = await response.text()
                    return [TextContent(
                        type="text",
                        text=f"Erreur API Red Bee (Status {response.status}): {error_text}"
                    )]
            
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de l'autocomplétion: {str(e)}"
        )]


async def get_epg_for_channel(
    config: RedBeeConfig,
    channelId: str,
    fromDate: Optional[str] = None,
    toDate: Optional[str] = None,
    includeUserData: Optional[bool] = True
) -> List[TextContent]:
    """Récupère le guide électronique des programmes (EPG) via l'endpoint v2"""
    
    try:
        async with RedBeeClient(config) as client:
            if not client.session_token:
                await client.authenticate_anonymous()
            
            # Utiliser l'endpoint v2 EPG selon la documentation
            if fromDate:
                endpoint = f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/epg/{channelId}/date/{fromDate}"
            else:
                # Use today's date as default
                from datetime import date
                today = date.today().strftime("%Y-%m-%d")
                endpoint = f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/epg/{channelId}/date/{today}"
            
            result = await client._make_request(
                "GET",
                endpoint,
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"EPG Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur API Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la récupération EPG: {str(e)}"
        )]


async def get_episodes_for_season(
    config: RedBeeConfig,
    seasonId: str,
    includeUserData: Optional[bool] = True
) -> List[TextContent]:
    """Récupère tous les épisodes d'une saison via l'endpoint v1"""
    
    try:
        async with RedBeeClient(config) as client:
            if not client.session_token:
                await client.authenticate_anonymous()
            
            # Utiliser l'endpoint v1 season selon la documentation
            result = await client._make_request(
                "GET",
                f"/v1/customer/{config.customer}/businessunit/{config.business_unit}/content/season/{seasonId}",
                params={
                    "onlyPublished": True,
                    "fieldSet": "ALL"
                },
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"Épisodes de la saison Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur API Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la récupération des épisodes: {str(e)}"
        )]


async def get_assets_by_tag(
    config: RedBeeConfig,
    tagType: str,
    assetType: Optional[str] = "MOVIE",
    onlyPublished: Optional[bool] = True
) -> List[TextContent]:
    """Récupère les tags uniques d'assets pour un type donné (SANS authentification)"""
    
    try:
        import aiohttp
        
        # Utiliser l'endpoint v1 public selon la documentation
        url = f"https://exposure.api.redbee.live/v1/customer/TV5MONDE/businessunit/TV5MONDEplus/tag/asset"
        
        params = {
            "tagType": tagType,
            "onlyPublished": "true" if onlyPublished else "false"
        }
        
        if assetType:
            params["assetType"] = assetType
        
        headers = {
            "accept": "application/json;charset=UTF-8"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return [TextContent(
                        type="text",
                        text=f"Tags {tagType} pour les assets Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
                    )]
                else:
                    error_text = await response.text()
                    return [TextContent(
                        type="text",
                        text=f"Erreur API Red Bee (Status {response.status}): {error_text}"
                    )]
            
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la récupération des tags: {str(e)}"
        )]


async def list_assets(
    config: RedBeeConfig,
    assetType: Optional[str] = None,
    assetTypes: Optional[List[str]] = None,
    sort: Optional[str] = None,
    query: Optional[str] = None,
    assetIds: Optional[List[str]] = None,
    parentalRatings: Optional[str] = None,
    pageSize: Optional[int] = 50,
    pageNumber: Optional[int] = 1,
    onlyPublished: Optional[bool] = True,
    playableWithinHours: Optional[int] = None,
    service: Optional[str] = None,
    allowedCountry: Optional[str] = None,
    deviceType: Optional[str] = None,
    deviceQuery: Optional[str] = None,
    publicationQuery: Optional[str] = None,
    products: Optional[List[str]] = None,
    missingFieldsFilter: Optional[str] = None,
    programsOnChannelIds: Optional[str] = None,
    includeTvShow: Optional[bool] = None,
    publicationStartsWithinDays: Optional[int] = None,
    publicationEndsWithinDays: Optional[int] = None,
    fieldSet: Optional[str] = "PARTIAL",
    includeFields: Optional[str] = None,
    excludeFields: Optional[str] = None
) -> List[TextContent]:
    """Liste des assets via l'endpoint principal (SANS authentification)"""
    
    try:
        import aiohttp
        
        # Utiliser l'endpoint v1 principal selon la documentation
        url = f"https://exposure.api.redbee.live/v1/customer/TV5MONDE/businessunit/TV5MONDEplus/content/asset"
        
        params = {
            "pageSize": pageSize,
            "pageNumber": pageNumber,
            "onlyPublished": "true" if onlyPublished else "false",
            "fieldSet": fieldSet
        }
        
                    # Add optional parameters only if provided
        if assetType:
            params["assetType"] = assetType
        if assetTypes:
            params["assetTypes"] = assetTypes
        if sort:
            params["sort"] = sort
        if query:
            params["query"] = query
        if assetIds:
            params["assetIds"] = assetIds
        if parentalRatings:
            params["parentalRatings"] = parentalRatings
        if playableWithinHours is not None:
            params["playableWithinHours"] = playableWithinHours
        if service:
            params["service"] = service
        if allowedCountry:
            params["allowedCountry"] = allowedCountry
        if deviceType:
            params["deviceType"] = deviceType
        if deviceQuery:
            params["deviceQuery"] = deviceQuery
        if publicationQuery:
            params["publicationQuery"] = publicationQuery
        if products:
            params["products"] = products
        if missingFieldsFilter:
            params["missingFieldsFilter"] = missingFieldsFilter
        if programsOnChannelIds:
            params["programsOnChannelIds"] = programsOnChannelIds
        if includeTvShow is not None:
            params["includeTvShow"] = includeTvShow
        if publicationStartsWithinDays is not None:
            params["publicationStartsWithinDays"] = publicationStartsWithinDays
        if publicationEndsWithinDays is not None:
            params["publicationEndsWithinDays"] = publicationEndsWithinDays
        if includeFields:
            params["includeFields"] = includeFields
        if excludeFields:
            params["excludeFields"] = excludeFields
        
        headers = {
            "accept": "application/json;charset=UTF-8"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Format the response
                    result = f"Liste des assets Red Bee Media:\n"
                    result += f"Page {data.get('pageNumber', 1)} sur {data.get('pageSize', pageSize)} éléments\n"
                    result += f"Total: {data.get('totalCount', 0)} assets\n\n"
                    
                    items = data.get('items', [])
                    for i, item in enumerate(items[:pageSize], 1):
                        result += f"{i}. **{item.get('localized', [{}])[0].get('title', 'Titre non disponible')}**\n"
                        result += f"   - ID: {item.get('assetId', 'N/A')}\n"
                        result += f"   - Type: {item.get('type', 'N/A')}\n"
                        if item.get('productionYear'):
                            result += f"   - Année: {item.get('productionYear')}\n"
                        if item.get('localized', [{}])[0].get('description'):
                            desc = item.get('localized', [{}])[0].get('description', '')[:100]
                            result += f"   - Description: {desc}...\n"
                        result += "\n"
                    
                    return [TextContent(type="text", text=result)]
                else:
                    error_text = await response.text()
                    return [TextContent(type="text", text=f"Erreur lors de la récupération des assets: {response.status} - {error_text}")]
                    
    except Exception as e:
        return [TextContent(type="text", text=f"Erreur lors de la récupération des assets: {str(e)}")]


# MCP Tool definitions
CONTENT_TOOLS = [
    Tool(
        name="get_public_asset_details",
        description="Récupère les détails d'un asset via l'endpoint public (sans authentification)",
        inputSchema={
            "type": "object",
            "properties": {
                "customer": {
                    "type": "string",
                    "description": "Customer ID (ex: TV5MONDE)"
                },
                "business_unit": {
                    "type": "string", 
                    "description": "Business Unit ID (ex: TV5MONDEplus)"
                },
                "assetId": {
                    "type": "string",
                    "description": "ID unique de l'asset"
                },
                "onlyPublished": {
                    "type": "boolean",
                    "description": "Uniquement les assets publiés",
                    "default": True
                },
                "fieldSet": {
                    "type": "string",
                    "description": "Ensemble de champs à retourner",
                    "default": "ALL"
                }
            },
            "required": ["customer", "business_unit", "assetId"]
        }
    ),
    Tool(
        name="search_content",
        description="Recherche du contenu dans la plateforme Red Bee par titre, genre, ou autres critères",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Terme de recherche (titre, acteur, réalisateur, etc.)"
                },
                "pageSize": {
                    "type": "integer",
                    "description": "Nombre de résultats par page",
                    "default": 50
                },
                "pageNumber": {
                    "type": "integer",
                    "description": "Numéro de page pour la pagination",
                    "default": 1
                },
                "sort": {
                    "type": "string",
                    "description": "Critère de tri"
                },
                "includeUserData": {
                    "type": "boolean",
                    "description": "Inclure les données utilisateur",
                    "default": True
                }
            },
            "required": []
        }
    ),
    Tool(
        name="get_asset_details",
        description="Récupère les détails complets d'un asset spécifique par son ID",
        inputSchema={
            "type": "object",
            "properties": {
                "assetId": {
                    "type": "string",
                    "description": "ID unique de l'asset"
                },
                "includeUserData": {
                    "type": "boolean",
                    "description": "Inclure les données utilisateur",
                    "default": True
                }
            },
            "required": ["assetId"]
        }
    ),
    Tool(
        name="get_playback_info",
        description="Récupère les informations de lecture (URL de stream, DRM, sous-titres) pour un asset",
        inputSchema={
            "type": "object",
            "properties": {
                "assetId": {
                    "type": "string",
                    "description": "ID unique de l'asset"
                },
                "sessionToken": {
                    "type": "string",
                    "description": "Token de session utilisateur"
                }
            },
            "required": ["assetId", "sessionToken"]
        }
    ),
    Tool(
        name="search_assets_autocomplete",
        description="Autocomplétion de recherche d'assets",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Terme de recherche pour l'autocomplétion"
                },
                "fieldSet": {
                    "type": "string",
                    "description": "Ensemble de champs à retourner",
                    "default": "ALL"
                }
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="get_epg_for_channel",
        description="Récupère le guide électronique des programmes (EPG) pour un canal spécifique",
        inputSchema={
            "type": "object",
            "properties": {
                "channelId": {
                    "type": "string",
                    "description": "ID unique du canal"
                },
                "fromDate": {
                    "type": "string",
                    "description": "Date de début (format ISO)"
                },
                "toDate": {
                    "type": "string", 
                    "description": "Date de fin (format ISO)"
                },
                "includeUserData": {
                    "type": "boolean",
                    "description": "Inclure les données utilisateur",
                    "default": True
                }
            },
            "required": ["channelId"]
        }
    ),
    Tool(
        name="get_episodes_for_season",
        description="Récupère tous les épisodes d'une saison",
        inputSchema={
            "type": "object",
            "properties": {
                "seasonId": {
                    "type": "string",
                    "description": "ID unique de la saison"
                },
                "includeUserData": {
                    "type": "boolean",
                    "description": "Inclure les données utilisateur",
                    "default": True
                }
            },
            "required": ["seasonId"]
        }
    ),
    Tool(
        name="get_assets_by_tag",
        description="Récupère les tags uniques d'assets pour un type donné (ex: origine pays pour les films)",
        inputSchema={
            "type": "object",
            "properties": {
                "tagType": {
                    "type": "string",
                    "description": "Type de tag à rechercher (ex: 'origin' pour pays d'origine)"
                },
                "assetType": {
                    "type": "string",
                    "description": "Type d'asset à filtrer",
                    "default": "MOVIE",
                    "enum": ["MOVIE", "TV_SHOW", "EPISODE", "CLIP", "TV_CHANNEL", "AD", "LIVE_EVENT", "COLLECTION", "PODCAST", "PODCAST_EPISODE", "EVENT", "OTHER"]
                },
                "onlyPublished": {
                    "type": "boolean",
                    "description": "Uniquement les assets publiés",
                    "default": True
                }
            },
            "required": ["tagType"]
        }
    ),
    Tool(
        name="list_assets",
        description="Liste des assets via l'endpoint principal (SANS authentification)",
        inputSchema={
            "type": "object",
            "properties": {
                "assetType": {
                    "type": "string",
                    "description": "Type d'asset à filtrer"
                },
                "assetTypes": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Types d'assets à filtrer"
                },
                "sort": {
                    "type": "string",
                    "description": "Critère de tri"
                },
                "query": {
                    "type": "string",
                    "description": "Terme de recherche"
                },
                "assetIds": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "IDs des assets à filtrer"
                },
                "parentalRatings": {
                    "type": "string",
                    "description": "Évaluation parentale"
                },
                "pageSize": {
                    "type": "integer",
                    "description": "Nombre de résultats par page",
                    "default": 50
                },
                "pageNumber": {
                    "type": "integer",
                    "description": "Numéro de page pour la pagination",
                    "default": 1
                },
                "onlyPublished": {
                    "type": "boolean",
                    "description": "Uniquement les assets publiés",
                    "default": True
                },
                "playableWithinHours": {
                    "type": "integer",
                    "description": "Durée jouable en heures"
                },
                "service": {
                    "type": "string",
                    "description": "Service"
                },
                "allowedCountry": {
                    "type": "string",
                    "description": "Pays autorisé"
                },
                "deviceType": {
                    "type": "string",
                    "description": "Type d'appareil"
                },
                "deviceQuery": {
                    "type": "string",
                    "description": "Requête d'appareil"
                },
                "publicationQuery": {
                    "type": "string",
                    "description": "Requête de publication"
                },
                "products": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Produits"
                },
                "missingFieldsFilter": {
                    "type": "string",
                    "description": "Filtre de champs manquants"
                },
                "programsOnChannelIds": {
                    "type": "string",
                    "description": "IDs des programmes sur le canal"
                },
                "includeTvShow": {
                    "type": "boolean",
                    "description": "Inclure les émissions de télévision"
                },
                "publicationStartsWithinDays": {
                    "type": "integer",
                    "description": "Jours avant publication"
                },
                "publicationEndsWithinDays": {
                    "type": "integer",
                    "description": "Jours après publication"
                },
                "fieldSet": {
                    "type": "string",
                    "description": "Ensemble de champs à retourner",
                    "default": "PARTIAL"
                },
                "includeFields": {
                    "type": "string",
                    "description": "Champs à inclure"
                },
                "excludeFields": {
                    "type": "string",
                    "description": "Champs à exclure"
                }
            },
            "required": []
        }
    )
] 

def get_all_content_tools() -> List[Tool]:
    """Return all content tools"""
    return CONTENT_TOOLS 