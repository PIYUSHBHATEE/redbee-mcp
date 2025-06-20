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
    config: RedBeeConfig,
    assetId: str,
    onlyPublished: Optional[bool] = True,
    fieldSet: Optional[str] = "ALL"
) -> List[TextContent]:
    """Retrieves asset details via public endpoint (without authentication)"""
    
    try:
        import aiohttp
        
        url = f"https://exposure.api.redbee.live/v1/customer/{config.customer}/businessunit/{config.business_unit}/content/asset/{assetId}"
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
                        text=f"Red Bee Media Asset Details (Public):\n{json.dumps(result, indent=2, ensure_ascii=False)}"
                    )]
                else:
                    error_text = await response.text()
                    return [TextContent(
                        type="text",
                        text=f"Red Bee API Error (Status {response.status}): {error_text}"
                    )]
                    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during retrieval: {str(e)}"
        )]



async def search_content_v2(
    config: RedBeeConfig,
    query: str,
    locale: Optional[List[str]] = None,
    types: Optional[str] = "MOVIE,TV_SHOW",
    tags: Optional[List[str]] = None,
    durationLower: Optional[int] = None,
    durationUpper: Optional[int] = None,
    subtitles: Optional[str] = None,
    schemes: Optional[List[str]] = None,
    parentalRatings: Optional[str] = None,
    onlyPublished: Optional[bool] = True,
    allowedCountry: Optional[str] = None,
    onlyDownloadable: Optional[bool] = None,
    pageSize: Optional[int] = 50,
    pageNumber: Optional[int] = 1,
    service: Optional[str] = None,
    fieldSet: Optional[str] = "ALL",
    includeFields: Optional[str] = None,
    excludeFields: Optional[str] = None
) -> List[TextContent]:
    """Search V2 - Free text query in selected fields in assets (including descriptions)"""
    
    try:
        import aiohttp
        
        url = f"https://exposure.api.redbee.live/v2/customer/{config.customer}/businessunit/{config.business_unit}/content/search/query/{query}"
        
        params = {
            "pageSize": pageSize,
            "pageNumber": pageNumber,
            "onlyPublished": str(onlyPublished).lower(),
            "fieldSet": fieldSet
        }
        
        # Ajouter les paramètres optionnels s'ils sont fournis
        if locale:
            for i, loc in enumerate(locale):
                params[f"locale[{i}]"] = loc
        if types:
            params["types"] = types
        if tags:
            for i, tag in enumerate(tags):
                params[f"tags[{i}]"] = tag
        if durationLower is not None:
            params["durationLower"] = durationLower
        if durationUpper is not None:
            params["durationUpper"] = durationUpper
        if subtitles:
            params["subtitles"] = subtitles
        if schemes:
            for i, scheme in enumerate(schemes):
                params[f"schemes[{i}]"] = scheme
        if parentalRatings:
            params["parentalRatings"] = parentalRatings
        if allowedCountry:
            params["allowedCountry"] = allowedCountry
        if onlyDownloadable is not None:
            params["onlyDownloadable"] = str(onlyDownloadable).lower()
        if service:
            params["service"] = service
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
                    result = await response.json()
                    return [TextContent(
                        type="text",
                        text=f"Red Bee Media Search V2 Results:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
                    )]
                else:
                    error_text = await response.text()
                    return [TextContent(
                        type="text",
                        text=f"Red Bee API Error (Status {response.status}): {error_text}"
                    )]
            
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during search V2: {str(e)}"
        )]


async def get_asset_details(
    config: RedBeeConfig,
    assetId: str,
    includeUserData: Optional[bool] = True
) -> List[TextContent]:
    """Retrieves complete asset details via v1 endpoint"""
    
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
                text=f"Red Bee Media Asset Details:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee API Error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during retrieval: {str(e)}"
        )]


async def get_playback_info(
    config: RedBeeConfig,
    assetId: str,
    sessionToken: str
) -> List[TextContent]:
    """Retrieves playback information via v2 play endpoint"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = sessionToken
            
            # Use v2 play endpoint according to documentation
            result = await client._make_request(
                "POST",
                f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/entitlement/{assetId}/play",
                data={},
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media Playback Information:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee API Error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during playback info retrieval: {str(e)}"
        )]


async def search_assets_autocomplete(
    config: RedBeeConfig,
    query: str,
    fieldSet: Optional[str] = "ALL"
) -> List[TextContent]:
    """Asset search autocompletion via v3 endpoint (WITHOUT authentication)"""
    
    try:
        import aiohttp
        
        # Utiliser l'endpoint v3 public selon la documentation avec les variables d'environnement
        url = f"https://exposure.api.redbee.live/v3/customer/{config.customer}/businessunit/{config.business_unit}/content/search/asset/title/autocomplete/{query}"
        
        params = {
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
                        text=f"Red Bee Media Autocomplete Results:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
                    )]
                else:
                    error_text = await response.text()
                    return [TextContent(
                        type="text",
                        text=f"Red Bee API Error (Status {response.status}): {error_text}"
                    )]
            
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during autocomplete: {str(e)}"
        )]


async def get_epg_for_channel(
    config: RedBeeConfig,
    channelId: str,
    fromDate: Optional[str] = None,
    toDate: Optional[str] = None,
    includeUserData: Optional[bool] = True
) -> List[TextContent]:
    """Retrieves Electronic Program Guide (EPG) via v2 endpoint"""
    
    try:
        async with RedBeeClient(config) as client:
            if not client.session_token:
                await client.authenticate_anonymous()
            
            # Use v2 EPG endpoint according to documentation
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
                text=f"Red Bee Media EPG:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee API Error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during EPG retrieval: {str(e)}"
        )]


async def get_episodes_for_season(
    config: RedBeeConfig,
    seasonId: str,
    includeUserData: Optional[bool] = True
) -> List[TextContent]:
    """Retrieves all episodes for a season via v1 endpoint"""
    
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
                text=f"Red Bee Media Season Episodes:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee API Error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during episodes retrieval: {str(e)}"
        )]


async def get_assets_by_tag(
    config: RedBeeConfig,
    tagType: str,
    assetType: Optional[str] = "MOVIE",
    onlyPublished: Optional[bool] = True
) -> List[TextContent]:
    """Retrieves unique asset tags for a given type (WITHOUT authentication)"""
    
    try:
        import aiohttp
        
        # Use public v1 endpoint according to documentation
        url = f"https://exposure.api.redbee.live/v1/customer/{config.customer}/businessunit/{config.business_unit}/tag/asset"
        
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
                        text=f"Red Bee Media {tagType} Tags for Assets:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
                    )]
                else:
                    error_text = await response.text()
                    return [TextContent(
                        type="text",
                        text=f"Red Bee API Error (Status {response.status}): {error_text}"
                    )]
            
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during tags retrieval: {str(e)}"
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
    """List assets via main endpoint (WITHOUT authentication)"""
    
    try:
        import aiohttp
        
        # Use main v1 endpoint according to documentation
        url = f"https://exposure.api.redbee.live/v1/customer/{config.customer}/businessunit/{config.business_unit}/content/asset"
        
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
                    result = f"Red Bee Media Assets List:\n"
                    result += f"Page {data.get('pageNumber', 1)} of {data.get('pageSize', pageSize)} items\n"
                    result += f"Total: {data.get('totalCount', 0)} assets\n\n"
                    
                    items = data.get('items', [])
                    for i, item in enumerate(items[:pageSize], 1):
                        result += f"{i}. **{item.get('localized', [{}])[0].get('title', 'Title not available')}**\n"
                        result += f"   - ID: {item.get('assetId', 'N/A')}\n"
                        result += f"   - Type: {item.get('type', 'N/A')}\n"
                        if item.get('productionYear'):
                            result += f"   - Year: {item.get('productionYear')}\n"
                        if item.get('localized', [{}])[0].get('description'):
                            desc = item.get('localized', [{}])[0].get('description', '')[:100]
                            result += f"   - Description: {desc}...\n"
                        result += "\n"
                    
                    return [TextContent(type="text", text=result)]
                else:
                    error_text = await response.text()
                    return [TextContent(type="text", text=f"Error retrieving assets: {response.status} - {error_text}")]
                    
    except Exception as e:
        return [TextContent(type="text", text=f"Error retrieving assets: {str(e)}")]





async def search_multi_v3(
    config: RedBeeConfig,
    query: str,
    types: Optional[str] = "MOVIE,TV_SHOW",
    locales: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    schemes: Optional[List[str]] = None,
    parentalRatings: Optional[str] = None,
    pageSize: Optional[int] = 50,
    pageNumber: Optional[int] = 1,
    onlyPublished: Optional[bool] = True
) -> List[TextContent]:
    """Multi-search V3 for assets, tags, and participants"""
    
    try:
        import aiohttp
        
        # Use v3 multi search endpoint
        url = f"https://exposure.api.redbee.live/v3/customer/{config.customer}/businessunit/{config.business_unit}/content/search/query/{query}"
        
        params = {
            "types": types,
            "pageSize": pageSize,
            "pageNumber": pageNumber,
            "onlyPublished": str(onlyPublished).lower(),
            "fieldSet": "ALL"
        }
        
        if locales:
            params["locales"] = locales
        if tags:
            params["tags"] = tags
        if schemes:
            params["schemes"] = schemes
        if parentalRatings:
            params["parentalRatings"] = parentalRatings
            
        headers = {
            "accept": "application/json;charset=UTF-8"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return [TextContent(
                        type="text",
                        text=f"Red Bee Media Multi-Search V3 Results:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
                    )]
                else:
                    error_text = await response.text()
                    return [TextContent(
                        type="text",
                        text=f"Red Bee API Error (Status {response.status}): {error_text}"
                    )]
                    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during multi-search: {str(e)}"
        )]


async def get_asset_collection_entries(
    config: RedBeeConfig,
    assetId: str,
    pageSize: Optional[int] = 50,
    pageNumber: Optional[int] = 1,
    onlyPublished: Optional[bool] = True,
    fieldSet: Optional[str] = "ALL"
) -> List[TextContent]:
    """Get collection entries for an asset collection"""
    
    try:
        async with RedBeeClient(config) as client:
            if not client.session_token:
                await client.authenticate_anonymous()
            
            params = {
                "pageSize": pageSize,
                "pageNumber": pageNumber,
                "onlyPublished": onlyPublished,
                "fieldSet": fieldSet
            }
            
            result = await client._make_request(
                "GET",
                f"/v1/customer/{config.customer}/businessunit/{config.business_unit}/content/asset/{assetId}/collectionentries",
                params=params,
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media Collection Entries:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee API Error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during collection entries retrieval: {str(e)}"
        )]


async def get_asset_thumbnail(
    config: RedBeeConfig,
    assetId: str,
    time: Optional[str] = None
) -> List[TextContent]:
    """Get thumbnail for an asset at a specific time"""
    
    try:
        import aiohttp
        
        # Use v1 thumbnail endpoint (returns 307 redirect)
        url = f"https://exposure.api.redbee.live/v1/customer/{config.customer}/businessunit/{config.business_unit}/content/asset/{assetId}/thumbnail"
        
        params = {}
        if time:
            params["time"] = time
            
        headers = {
            "accept": "application/json;charset=UTF-8"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, allow_redirects=False) as response:
                if response.status == 307:
                    thumbnail_url = response.headers.get("Location")
                    return [TextContent(
                        type="text",
                        text=f"Red Bee Media Asset Thumbnail URL:\n{thumbnail_url}"
                    )]
                elif response.status == 200:
                    result = await response.json()
                    return [TextContent(
                        type="text",
                        text=f"Red Bee Media Asset Thumbnail Info:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
                    )]
                else:
                    error_text = await response.text()
                    return [TextContent(
                        type="text",
                        text=f"Red Bee API Error (Status {response.status}): {error_text}"
                    )]
                    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during thumbnail retrieval: {str(e)}"
        )]


async def get_seasons_for_series(
    config: RedBeeConfig,
    assetId: str,
    pageSize: Optional[int] = 50,
    pageNumber: Optional[int] = 1,
    onlyPublished: Optional[bool] = True,
    fieldSet: Optional[str] = "ALL"
) -> List[TextContent]:
    """Get all seasons for a TV series"""
    
    try:
        async with RedBeeClient(config) as client:
            if not client.session_token:
                await client.authenticate_anonymous()
            
            params = {
                "pageSize": pageSize,
                "pageNumber": pageNumber,
                "onlyPublished": onlyPublished,
                "fieldSet": fieldSet
            }
            
            result = await client._make_request(
                "GET",
                f"/v1/customer/{config.customer}/businessunit/{config.business_unit}/content/asset/{assetId}/season",
                params=params,
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media Seasons for Series:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee API Error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during seasons retrieval: {str(e)}"
        )]


# MCP Tool definitions
CONTENT_TOOLS = [
    Tool(
        name="get_public_asset_details",
        description="Retrieves asset details via public endpoint (without authentication)",
        inputSchema={
            "type": "object",
            "properties": {
                "assetId": {
                    "type": "string",
                    "description": "Unique asset ID"
                },
                "onlyPublished": {
                    "type": "boolean",
                    "description": "Only published assets",
                    "default": True
                },
                "fieldSet": {
                    "type": "string",
                    "description": "Set of fields to return",
                    "default": "ALL"
                }
            },
            "required": ["assetId"]
        }
    ),

    Tool(
        name="search_content_v2",
        description="Search V2 - Free text query in selected fields in assets (including descriptions). Perfect for searching actors, directors, or content in descriptions.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term to find in asset fields including descriptions (e.g., actor names, director names, etc.)"
                },
                "locale": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Locales to search in (e.g., ['fr', 'en'])"
                },
                "types": {
                    "type": "string",
                    "description": "Asset types to search (comma-separated)",
                    "default": "MOVIE,TV_SHOW"
                },
                "tags": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Tags to filter by"
                },
                "durationLower": {
                    "type": "integer",
                    "description": "Minimum duration in seconds"
                },
                "durationUpper": {
                    "type": "integer",
                    "description": "Maximum duration in seconds"
                },
                "subtitles": {
                    "type": "string",
                    "description": "Subtitle language filter"
                },
                "schemes": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Tag schemes to search"
                },
                "parentalRatings": {
                    "type": "string",
                    "description": "Parental rating filter (COUNTRY:RATING format)"
                },
                "onlyPublished": {
                    "type": "boolean",
                    "description": "Only published content",
                    "default": True
                },
                "allowedCountry": {
                    "type": "string",
                    "description": "Country filter"
                },
                "onlyDownloadable": {
                    "type": "boolean",
                    "description": "Only downloadable content"
                },
                "pageSize": {
                    "type": "integer",
                    "description": "Number of results per page",
                    "default": 50
                },
                "pageNumber": {
                    "type": "integer",
                    "description": "Page number for pagination",
                    "default": 1
                },
                "service": {
                    "type": "string",
                    "description": "Service filter"
                },
                "fieldSet": {
                    "type": "string",
                    "description": "Field set to return",
                    "default": "ALL"
                },
                "includeFields": {
                    "type": "string",
                    "description": "Comma separated list of field names to include"
                },
                "excludeFields": {
                    "type": "string",
                    "description": "Comma separated list of field names to exclude"
                }
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="get_asset_details",
        description="Retrieves complete details of a specific asset by its ID",
        inputSchema={
            "type": "object",
            "properties": {
                "assetId": {
                    "type": "string",
                    "description": "Unique asset ID"
                },
                "includeUserData": {
                    "type": "boolean",
                    "description": "Include user data",
                    "default": True
                }
            },
            "required": ["assetId"]
        }
    ),
    Tool(
        name="get_playback_info",
        description="Retrieves playback information (stream URL, DRM, subtitles) for an asset",
        inputSchema={
            "type": "object",
            "properties": {
                "assetId": {
                    "type": "string",
                    "description": "Unique asset ID"
                },
                "sessionToken": {
                    "type": "string",
                    "description": "User session token"
                }
            },
            "required": ["assetId", "sessionToken"]
        }
    ),
    Tool(
        name="search_assets_autocomplete",
        description="Asset search autocompletion",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term for autocompletion"
                },
                "fieldSet": {
                    "type": "string",
                    "description": "Set of fields to return",
                    "default": "ALL"
                }
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="get_epg_for_channel",
        description="Retrieves Electronic Program Guide (EPG) for a specific channel",
        inputSchema={
            "type": "object",
            "properties": {
                "channelId": {
                    "type": "string",
                    "description": "Unique channel ID"
                },
                "fromDate": {
                    "type": "string",
                    "description": "Start date (ISO format)"
                },
                "toDate": {
                    "type": "string", 
                    "description": "End date (ISO format)"
                },
                "includeUserData": {
                    "type": "boolean",
                    "description": "Include user data",
                    "default": True
                }
            },
            "required": ["channelId"]
        }
    ),
    Tool(
        name="get_episodes_for_season",
        description="Retrieves all episodes for a season",
        inputSchema={
            "type": "object",
            "properties": {
                "seasonId": {
                    "type": "string",
                    "description": "Unique season ID"
                },
                "includeUserData": {
                    "type": "boolean",
                    "description": "Include user data",
                    "default": True
                }
            },
            "required": ["seasonId"]
        }
    ),
    Tool(
        name="get_assets_by_tag",
        description="Retrieves unique asset tags for a given type (e.g., country origin for movies)",
        inputSchema={
            "type": "object",
            "properties": {
                "tagType": {
                    "type": "string",
                    "description": "Tag type to search for (e.g., 'origin' for country origin)"
                },
                "assetType": {
                    "type": "string",
                    "description": "Asset type to filter",
                    "default": "MOVIE",
                    "enum": ["MOVIE", "TV_SHOW", "EPISODE", "CLIP", "TV_CHANNEL", "AD", "LIVE_EVENT", "COLLECTION", "PODCAST", "PODCAST_EPISODE", "EVENT", "OTHER"]
                },
                "onlyPublished": {
                    "type": "boolean",
                    "description": "Only published assets",
                    "default": True
                }
            },
            "required": ["tagType"]
        }
    ),
    Tool(
        name="list_assets",
        description="List assets via main endpoint (WITHOUT authentication)",
        inputSchema={
            "type": "object",
            "properties": {
                "assetType": {
                    "type": "string",
                    "description": "Asset type to filter"
                },
                "assetTypes": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Asset types to filter"
                },
                "sort": {
                    "type": "string",
                    "description": "Sort criteria"
                },
                "query": {
                    "type": "string",
                    "description": "Search term"
                },
                "assetIds": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Asset IDs to filter"
                },
                "parentalRatings": {
                    "type": "string",
                    "description": "Parental rating"
                },
                "pageSize": {
                    "type": "integer",
                    "description": "Number of results per page",
                    "default": 50
                },
                "pageNumber": {
                    "type": "integer",
                    "description": "Page number for pagination",
                    "default": 1
                },
                "onlyPublished": {
                    "type": "boolean",
                    "description": "Only published assets",
                    "default": True
                },
                "playableWithinHours": {
                    "type": "integer",
                    "description": "Playable duration in hours"
                },
                "service": {
                    "type": "string",
                    "description": "Service"
                },
                "allowedCountry": {
                    "type": "string",
                    "description": "Allowed country"
                },
                "deviceType": {
                    "type": "string",
                    "description": "Device type"
                },
                "deviceQuery": {
                    "type": "string",
                    "description": "Device query"
                },
                "publicationQuery": {
                    "type": "string",
                    "description": "Publication query"
                },
                "products": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Products"
                },
                "missingFieldsFilter": {
                    "type": "string",
                    "description": "Missing fields filter"
                },
                "programsOnChannelIds": {
                    "type": "string",
                    "description": "Program IDs on channel"
                },
                "includeTvShow": {
                    "type": "boolean",
                    "description": "Include TV shows"
                },
                "publicationStartsWithinDays": {
                    "type": "integer",
                    "description": "Days before publication"
                },
                "publicationEndsWithinDays": {
                    "type": "integer",
                    "description": "Days after publication"
                },
                "fieldSet": {
                    "type": "string",
                    "description": "Set of fields to return",
                    "default": "PARTIAL"
                },
                "includeFields": {
                    "type": "string",
                    "description": "Fields to include"
                },
                "excludeFields": {
                    "type": "string",
                    "description": "Fields to exclude"
                }
            },
            "required": []
        }
    ),

    Tool(
        name="search_multi_v3",
        description="Multi-search V3 for assets, tags, and participants with advanced filtering",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "types": {
                    "type": "string",
                    "description": "Asset types to search (comma-separated)",
                    "default": "MOVIE,TV_SHOW"
                },
                "locales": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Locales to search in"
                },
                "tags": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Tags to filter by"
                },
                "schemes": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Tag schemes to search"
                },
                "parentalRatings": {
                    "type": "string",
                    "description": "Parental rating filter"
                },
                "pageSize": {
                    "type": "integer",
                    "description": "Number of results per page",
                    "default": 50
                },
                "pageNumber": {
                    "type": "integer",
                    "description": "Page number for pagination",
                    "default": 1
                },
                "onlyPublished": {
                    "type": "boolean",
                    "description": "Only published content",
                    "default": True
                }
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="get_asset_collection_entries",
        description="Get collection entries for an asset collection",
        inputSchema={
            "type": "object",
            "properties": {
                "assetId": {
                    "type": "string",
                    "description": "Collection asset ID"
                },
                "pageSize": {
                    "type": "integer",
                    "description": "Number of results per page",
                    "default": 50
                },
                "pageNumber": {
                    "type": "integer",
                    "description": "Page number for pagination",
                    "default": 1
                },
                "onlyPublished": {
                    "type": "boolean",
                    "description": "Only published assets",
                    "default": True
                },
                "fieldSet": {
                    "type": "string",
                    "description": "Set of fields to return",
                    "default": "ALL"
                }
            },
            "required": ["assetId"]
        }
    ),
    Tool(
        name="get_asset_thumbnail",
        description="Get thumbnail URL for an asset at a specific time",
        inputSchema={
            "type": "object",
            "properties": {
                "assetId": {
                    "type": "string",
                    "description": "Asset ID to get thumbnail for"
                },
                "time": {
                    "type": "string",
                    "description": "Time position for thumbnail (ISO format or duration like PT30M20S)"
                }
            },
            "required": ["assetId"]
        }
    ),
    Tool(
        name="get_seasons_for_series",
        description="Get all seasons for a TV series",
        inputSchema={
            "type": "object",
            "properties": {
                "assetId": {
                    "type": "string",
                    "description": "TV series asset ID"
                },
                "pageSize": {
                    "type": "integer",
                    "description": "Number of results per page",
                    "default": 50
                },
                "pageNumber": {
                    "type": "integer",
                    "description": "Page number for pagination",
                    "default": 1
                },
                "onlyPublished": {
                    "type": "boolean",
                    "description": "Only published seasons",
                    "default": True
                },
                "fieldSet": {
                    "type": "string",
                    "description": "Set of fields to return",
                    "default": "ALL"
                }
            },
            "required": ["assetId"]
        }
    )
] 

def get_all_content_tools() -> List[Tool]:
    """Return all content tools"""
    return CONTENT_TOOLS 