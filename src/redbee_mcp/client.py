"""
Client API pour Red Bee Media OTT Platform
Basé sur la documentation officielle : https://redbee.live/docs/
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
import httpx
import json
from datetime import datetime, timedelta

from .models import (
    RedBeeConfig, 
    AuthenticationResponse, 
    Asset, 
    PlaybackInfo, 
    SearchResult, 
    UserEntitlement,
    ContentAnalytics,
    ViewingHistory,
    PlatformMetrics,
    BusinessUnitInfo
)

# Configure logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/redbee-mcp.log'),
    ]
)
logger = logging.getLogger(__name__)


class RedBeeAPIError(Exception):
    """Exception pour les erreurs de l'API Red Bee"""
    def __init__(self, message: str, status_code: Optional[int] = None, error_code: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class RedBeeClient:
    """Red Bee Media API client with authentication support"""
    
    def __init__(self, config: RedBeeConfig):
        self.config = config
        self.session_token: Optional[str] = config.session_token
        self.device_id: Optional[str] = config.device_id
        self.username: Optional[str] = config.username
        
        # Default timeout configuration
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        
        # Create base client configuration
        self.client_config = {
            "timeout": self.timeout,
            "follow_redirects": True,
            "verify": True
        }
        
        # Different API URLs
        self.auth_url = f"{config.exposure_base_url}/auth"
        self.entitlement_url = f"{config.exposure_base_url}/entitlement" 
        self.content_url = f"{config.exposure_base_url}/content"
        
        # Session data
        self.account_id: Optional[str] = None
        self.account_id: Optional[str] = None

    def _get_base_headers(self) -> Dict[str, str]:
        """Get base headers for requests"""
        return {
            "User-Agent": "RedbeePlayer/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        headers = self._get_base_headers()
        if self.session_token:
            headers["Authorization"] = f"Bearer {self.session_token}"
        return headers

    def _get_public_headers(self) -> Dict[str, str]:
        """Minimal headers for public requests (like the curl that works)"""
        return {
            "User-Agent": "RedbeePlayer/1.0",
            "Accept": "application/json"
        }

    async def _make_request(
        self, 
        method: str, 
        url: str, 
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        use_auth: bool = True
    ) -> Dict[str, Any]:
        """Make HTTP request with proper error handling"""
        
        if headers is None:
            if use_auth:
                headers = self._get_auth_headers()
            else:
                # For GET requests without authentication, use a simpler approach
                headers = self._get_public_headers()
        
        try:
            async with httpx.AsyncClient(**self.client_config) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=headers, params=params, json=json_data)
                elif method.upper() == "PUT":
                    response = await client.put(url, headers=headers, params=params, json=json_data)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=headers, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                logger.info(f"REQUEST: {method} {url} -> {response.status_code}")
                
                # Handle different response types
                if response.status_code == 204:
                    return {"success": True, "message": "No content"}
                
                if response.headers.get("content-type", "").startswith("application/json"):
                    return response.json()
                else:
                    return {"text": response.text, "status_code": response.status_code}
                    
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise Exception(f"HTTP request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    # Authentication methods
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """User login with username and password"""
        login_data = {
            "credentials": {
                "username": username,
                "password": password
            },
            "device": {
                "deviceId": self.device_id,
                "name": "Red Bee MCP Client"
            },
            "customer": self.config.customer,
            "businessUnit": self.config.business_unit
        }
        
        url = f"{self.auth_url}/{self.config.customer}/{self.config.business_unit}/login"
        result = await self._make_request("POST", url, json_data=login_data, use_auth=False)
        
        # Update token for subsequent requests
        if "sessionToken" in result:
            self.session_token = result["sessionToken"]
            if "accountId" in result:
                self.account_id = result["accountId"]
        
        return result

    async def create_anonymous_session(self) -> Dict[str, Any]:
        """Create an anonymous session"""
        session_data = {
            "device": {
                "deviceId": self.device_id,
                "name": "Red Bee MCP Client"
            },
            "customer": self.config.customer,
            "businessUnit": self.config.business_unit
        }
        
        url = f"{self.auth_url}/{self.config.customer}/{self.config.business_unit}/session"
        result = await self._make_request("POST", url, json_data=session_data, use_auth=False)
        
        # Update token for subsequent requests
        if "sessionToken" in result:
            self.session_token = result["sessionToken"]
        
        return result

    async def search_assets_autocomplete(self, query: str, locale: str = "en") -> Dict[str, Any]:
        """Search assets with autocomplete - special handling for this problematic endpoint"""
        
        # Use direct call with a new clean client to avoid header issues
        url = f"{self.content_url}/{self.config.customer}/{self.config.business_unit}/search/autocomplete"
        params = {"q": query, "locale": locale}
        headers = self._get_public_headers()
        
        logger.info(f"SEARCH AUTOCOMPLETE - URL: {url}")
        logger.info(f"SEARCH AUTOCOMPLETE - Headers: {headers}")
        logger.info(f"SEARCH AUTOCOMPLETE - Params: {params}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response_obj = await client.get(url, headers=headers, params=params)
                
                logger.info(f"DIRECT REQUEST: GET {url} -> {response_obj.status_code}")
                
                if response_obj.status_code != 200:
                    error_text = response_obj.text
                    logger.error(f"ERROR RESPONSE: {error_text}")
                    return {
                        "error": f"HTTP {response_obj.status_code}",
                        "message": error_text,
                        "url": url,
                        "params": params
                    }
                
                return response_obj.json()
                
        except Exception as e:
            logger.error(f"Request error: {e}")
            return {
                "error": "Request failed",
                "message": str(e),
                "url": url,
                "params": params
            }

    async def search_content(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search content in the catalog"""
        url = f"{self.content_url}/{self.config.customer}/{self.config.business_unit}/search"
        
        params = {"q": query}
        params.update(kwargs)
        
        result = await self._make_request("GET", url, params=params, use_auth=False)
        
        # Different processing depending on response type (autocomplete vs asset listing)
        if isinstance(result, list):
            # Autocomplete endpoint response (direct list)
            return {
                "items": result,
                "total": len(result),
                "query": query,
                "source": "autocomplete"
            }
        elif isinstance(result, dict):
            # Standard search response
            if "hits" in result:
                items = []
                for hit in result["hits"]:
                    if "_source" in hit:
                        item = hit["_source"]
                        # Add relevance score if available
                        if "_score" in hit:
                            item["_relevanceScore"] = hit["_score"]
                        items.append(item)
                    else:
                        items.append(hit)
                
                return {
                    "items": items,
                    "total": result.get("total", len(items)),
                    "query": query,
                    "took": result.get("took"),
                    "source": "search"
                }
            elif "items" in result:
                # Asset endpoint response (structure with items)
                return {
                    "items": result["items"],
                    "total": result.get("totalCount", len(result["items"])),
                    "query": query,
                    "source": "assets"
                }
            else:
                # Return as is if unrecognized format
                return result
        else:
            return result

    async def get_asset_details(self, asset_id: str) -> Dict[str, Any]:
        """Get asset details by ID"""
        url = f"{self.content_url}/{self.config.customer}/{self.config.business_unit}/asset/{asset_id}"
        return await self._make_request("GET", url, use_auth=False)

    async def get_playback_info(self, asset_id: str, **kwargs) -> Dict[str, Any]:
        """Get playback information for an asset"""
        url = f"{self.entitlement_url}/{self.config.customer}/{self.config.business_unit}/entitlement/{asset_id}/play"
        
        params = {}
        params.update(kwargs)
        
        result = await self._make_request("POST", url, json_data=params)
        
        # Process playback info
        if "formats" in result:
            # Find preferred streaming format
            preferred_format = None
            for fmt in result["formats"]:
                if fmt.get("format") == "DASH":
                    preferred_format = fmt
                    break
            
            if not preferred_format and result["formats"]:
                preferred_format = result["formats"][0]
            
            if preferred_format:
                result["preferredPlaybackUrl"] = preferred_format.get("mediaLocator")
        
        return result

    # Content methods
    async def list_assets(self, **kwargs) -> Dict[str, Any]:
        """List available assets"""
        url = f"{self.content_url}/{self.config.customer}/{self.config.business_unit}/asset"
        
        params = {}
        params.update(kwargs)
        
        return await self._make_request("GET", url, params=params, use_auth=False)

    async def get_public_asset_details(self, asset_id: str) -> Dict[str, Any]:
        """Get public asset details (no authentication required)"""
        url = f"{self.content_url}/{self.config.customer}/{self.config.business_unit}/asset/{asset_id}/publicDetails"
        return await self._make_request("GET", url, use_auth=False)

    async def get_assets_by_tag(self, tag: str, **kwargs) -> Dict[str, Any]:
        """Get assets by tag"""
        url = f"{self.content_url}/{self.config.customer}/{self.config.business_unit}/asset"
        
        params = {"tag": tag}
        params.update(kwargs)
        
        return await self._make_request("GET", url, params=params, use_auth=False)

    async def get_epg_for_channel(self, channel_id: str, **kwargs) -> Dict[str, Any]:
        """Get Electronic Program Guide for a channel"""
        url = f"{self.content_url}/{self.config.customer}/{self.config.business_unit}/epg/{channel_id}"
        
        params = {}
        params.update(kwargs)
        
        return await self._make_request("GET", url, params=params, use_auth=False)

    async def get_episodes_for_season(self, season_id: str, **kwargs) -> Dict[str, Any]:
        """Get episodes for a specific season"""
        url = f"{self.content_url}/{self.config.customer}/{self.config.business_unit}/asset/{season_id}/episode"
        
        params = {}
        params.update(kwargs)
        
        return await self._make_request("GET", url, params=params, use_auth=False)

    # =====================================
    # User Entitlements
    # =====================================
    
    async def get_user_entitlements(self, user_id: str) -> List[UserEntitlement]:
        """Retrieves user entitlements"""
        
        response = await self._make_request(
            "GET",
            f"/customer/{self.config.customer}/businessunit/{self.config.business_unit}/entitlement/user/{user_id}"
        )
        
        entitlements = []
        for item in response.get("entitlements", []):
            entitlement = UserEntitlement(
                user_id=user_id,
                asset_id=item["assetId"],
                entitlement_type=item.get("type", "unknown"),
                expires_at=item.get("expiresAt"),
                restrictions=item.get("restrictions", {})
            )
            entitlements.append(entitlement)
        
        return entitlements
    
    # =====================================
    # Analytics
    # =====================================
    
    async def get_content_analytics(
        self, 
        asset_id: str, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> ContentAnalytics:
        """Retrieves content analytics"""
        
        params = {
            "assetId": asset_id
        }
        
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        
        response = await self._make_request(
            "GET",
            f"/customer/{self.config.customer}/businessunit/{self.config.business_unit}/analytics/content",
            params=params,
            base_url=self.analytics_url
        )
        
        return ContentAnalytics(
            asset_id=asset_id,
            period_start=response.get("periodStart"),
            period_end=response.get("periodEnd"),
            total_views=response.get("totalViews", 0),
            unique_viewers=response.get("uniqueViewers", 0),
            total_watch_time=response.get("totalWatchTime", 0),
            average_watch_time=response.get("averageWatchTime", 0.0),
            completion_rate=response.get("completionRate", 0.0),
            geographic_distribution=response.get("geographicDistribution", {}),
            device_distribution=response.get("deviceDistribution", {})
        )
    
    async def get_user_viewing_history(
        self, 
        user_id: str, 
        page: int = 1, 
        per_page: int = 20
    ) -> List[ViewingHistory]:
        """Retrieves user viewing history"""
        
        params = {
            "userId": user_id,
            "pageSize": per_page,
            "pageNumber": page
        }
        
        response = await self._make_request(
            "GET",
            f"/customer/{self.config.customer}/businessunit/{self.config.business_unit}/analytics/viewing-history",
            params=params,
            base_url=self.analytics_url
        )
        
        history = []
        for item in response.get("items", []):
            history_item = ViewingHistory(
                user_id=user_id,
                asset_id=item["assetId"],
                started_at=item["startedAt"],
                ended_at=item.get("endedAt"),
                watch_duration=item.get("watchDuration", 0),
                completion_percentage=item.get("completionPercentage", 0.0),
                device_type=item.get("deviceType"),
                quality=item.get("quality")
            )
            history.append(history_item)
        
        return history
    
    async def get_platform_metrics(
        self, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> PlatformMetrics:
        """Retrieves platform global metrics"""
        
        params = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        
        response = await self._make_request(
            "GET",
            f"/customer/{self.config.customer}/businessunit/{self.config.business_unit}/analytics/platform",
            params=params,
            base_url=self.analytics_url
        )
        
        return PlatformMetrics(
            period_start=response.get("periodStart"),
            period_end=response.get("periodEnd"),
            total_users=response.get("totalUsers", 0),
            active_users=response.get("activeUsers", 0),
            total_content_hours=response.get("totalContentHours", 0.0),
            total_watch_hours=response.get("totalWatchHours", 0.0),
            popular_content=response.get("popularContent", []),
            user_engagement=response.get("userEngagement", {})
        )
    
    # =====================================
    # Business Unit Configuration
    # =====================================
    
    async def get_business_unit_info(self) -> BusinessUnitInfo:
        """Retrieves business unit configuration information"""
        
        response = await self._make_request(
            "GET",
            f"/customer/{self.config.customer}/businessunit/{self.config.business_unit}/config"
        )
        
        return BusinessUnitInfo(
            customer=self.config.customer,
            business_unit=self.config.business_unit,
            name=response.get("name", ""),
            description=response.get("description"),
            features=response.get("features", []),
            settings=response.get("settings", {}),
            locale=response.get("locale", "en"),
            timezone=response.get("timezone", "UTC")
        ) 