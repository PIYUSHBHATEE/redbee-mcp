"""
Client API pour Red Bee Media OTT Platform
Basé sur la documentation officielle : https://redbee.live/docs/
"""

import httpx
from typing import Optional, Dict, List, Any
from urllib.parse import urljoin
import logging

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

logger = logging.getLogger(__name__)


class RedBeeAPIError(Exception):
    """Exception pour les erreurs de l'API Red Bee"""
    def __init__(self, message: str, status_code: Optional[int] = None, error_code: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class RedBeeClient:
    """Client pour interagir avec les APIs Red Bee Media"""
    
    def __init__(self, config: RedBeeConfig):
        self.config = config
        self.session_token = config.session_token
        self.device_id = config.device_id
        
        # URLs des différentes APIs
        self.exposure_url = config.exposure_base_url
        self.analytics_url = config.exposure_base_url.replace("exposure", "eventsink")
        
        # Client HTTP
        self.client = httpx.AsyncClient(timeout=config.timeout)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """Construit les headers pour les requêtes"""
        if include_auth and self.session_token:
            headers = {
                "Accept": "application/json",
                "EMP-Auth": self.session_token
            }
        else:
            # Headers minimalistes pour les requêtes publiques (comme le curl qui fonctionne)
            headers = {
                "Accept": "application/json"
            }
            
        return headers
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        base_url: Optional[str] = None,
        include_auth: bool = True
    ) -> Dict[str, Any]:
        """Effectue une requête HTTP vers l'API"""
        
        url = urljoin(base_url or self.exposure_url, endpoint)
        headers = self._get_headers(include_auth)
        
        try:
            # Pour les requêtes GET sans authentification, on utilise une approche plus simple
            if method == "GET" and not include_auth and not data:
                response = await self.client.get(url, params=params, headers=headers)
            else:
                response = await self.client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params
                )
            
            logger.info(f"REQUEST: {method} {url} -> {response.status_code}")
            
            if response.status_code >= 400:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    pass
                
                raise RedBeeAPIError(
                    message=error_data.get("message", f"HTTP {response.status_code}"),
                    status_code=response.status_code,
                    error_code=error_data.get("error_code")
                )
            
            return response.json()
            
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise RedBeeAPIError(f"Erreur de requête: {e}")
    
    # =====================================
    # Authentication
    # =====================================
    
    async def authenticate(self, username: Optional[str] = None, password: Optional[str] = None) -> AuthenticationResponse:
        """Authentifie un utilisateur et obtient un token de session"""
        
        if username and password:
            # Authentification utilisateur via v3
            auth_data = {
                "credentials": {
                    "username": username,
                    "password": password
                },
                "device": {
                    "deviceId": self.device_id or f"web_{self.config.customer}",
                    "name": "Web Browser",
                    "type": "WEB"
                }
            }
            
            response = await self._make_request(
                "POST", 
                f"/v3/customer/{self.config.customer}/businessunit/{self.config.business_unit}/auth/login",
                data=auth_data,
                include_auth=False
            )
        else:
            # Session anonyme via v2
            auth_data = {
                "device": {
                    "deviceId": self.device_id or f"anon_{self.config.customer}",
                    "type": "WEB"
                }
            }
            
            response = await self._make_request(
                "POST", 
                f"/v2/customer/{self.config.customer}/businessunit/{self.config.business_unit}/auth/anonymous",
                data=auth_data,
                include_auth=False
            )
        
        auth_response = AuthenticationResponse(
            session_token=response["sessionToken"],
            device_id=response.get("deviceId", self.device_id or ""),
            expires_at=response.get("expiresAt")
        )
        
        # Met à jour le token pour les requêtes suivantes
        self.session_token = auth_response.session_token
        self.device_id = auth_response.device_id
        
        return auth_response
    
    async def authenticate_anonymous(self) -> AuthenticationResponse:
        """Authentification anonyme"""
        return await self.authenticate()
    
    # =====================================
    # Asset Management
    # =====================================
    
    async def search_assets(
        self, 
        query: Optional[str] = None,
        content_type: Optional[str] = None,
        genre: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None
    ) -> SearchResult:
        """Recherche des assets"""
        
        # Utiliser l'endpoint autocomplete pour la recherche
        if query:
            # Appel direct avec un nouveau client propre pour éviter les problèmes de headers
            url = f"{self.exposure_url}/v1/customer/{self.config.customer}/businessunit/{self.config.business_unit}/content/search/autocomplete/{query}"
            headers = {"accept": "application/json"}
            params = {"locale": "fr"}
            
            logger.info(f"SEARCH AUTOCOMPLETE - URL: {url}")
            logger.info(f"SEARCH AUTOCOMPLETE - Headers: {headers}")
            logger.info(f"SEARCH AUTOCOMPLETE - Params: {params}")
            
            try:
                # Utiliser un nouveau client HTTP propre
                async with httpx.AsyncClient() as clean_client:
                    response_obj = await clean_client.get(url, params=params, headers=headers)
                    logger.info(f"DIRECT REQUEST: GET {url} -> {response_obj.status_code}")
                    
                    if response_obj.status_code >= 400:
                        error_text = response_obj.text
                        logger.error(f"ERROR RESPONSE: {error_text}")
                        raise RedBeeAPIError(
                            message=error_text,
                            status_code=response_obj.status_code
                        )
                    
                    response = response_obj.json()
            except httpx.RequestError as e:
                logger.error(f"Request error: {e}")
                raise RedBeeAPIError(f"Erreur de requête: {e}")
        else:
            # Fallback vers l'endpoint asset pour lister le contenu
            params = {
                "pageSize": per_page,
                "pageNumber": page,
                "locale": "fr"
            }
            
            if content_type:
                params["contentType"] = content_type
            if genre:
                params["genre"] = genre
            if sort_by:
                params["sortBy"] = sort_by
            
            response = await self._make_request(
                "GET",
                f"/v1/customer/{self.config.customer}/businessunit/{self.config.business_unit}/content/asset",
                params=params
            )
        
        assets = []
        
        # Traitement différent selon le type de réponse (autocomplete vs asset listing)
        if query and isinstance(response, list):
            # Réponse de l'endpoint autocomplete (liste directe)
            for item in response:
                asset = Asset(
                    asset_id=item["assetId"],
                    title=item.get("text", ""),
                    description=None,
                    duration=None,
                    content_type=None,
                    media_type=None,
                    genre=[],
                    release_date=None,
                    rating=None,
                    language=None,
                    subtitle_languages=[],
                    poster_url=None,
                    thumbnail_url=None,
                    trailer_url=None,
                    tags=[],
                    external_references={}
                )
                assets.append(asset)
            
            return SearchResult(
                total_results=len(response),
                page=1,
                per_page=len(response),
                total_pages=1,
                assets=assets
            )
        else:
            # Réponse de l'endpoint asset (structure avec items)
            for item in response.get("items", []):
                asset = Asset(
                    asset_id=item["assetId"],
                    title=item.get("title", ""),
                    description=item.get("description"),
                    duration=item.get("duration"),
                    content_type=item.get("contentType"),
                    media_type=item.get("mediaType"),
                    genre=item.get("genre", []),
                    release_date=item.get("releaseDate"),
                    rating=item.get("rating"),
                    language=item.get("language"),
                    subtitle_languages=item.get("subtitleLanguages", []),
                    poster_url=item.get("posterUrl"),
                    thumbnail_url=item.get("thumbnailUrl"),
                    trailer_url=item.get("trailerUrl"),
                    tags=item.get("tags", []),
                    external_references=item.get("externalReferences", {})
                )
                assets.append(asset)
            
            return SearchResult(
                total_results=response.get("totalCount", 0),
                page=page,
                per_page=per_page,
                total_pages=response.get("totalPages", 1),
                assets=assets
            )
    
    async def get_asset(self, asset_id: str) -> Asset:
        """Récupère les détails d'un asset"""
        
        response = await self._make_request(
            "GET",
            f"/v1/customer/{self.config.customer}/businessunit/{self.config.business_unit}/content/asset/{asset_id}",
            params={"locale": "fr"}
        )
        
        return Asset(
            asset_id=response["assetId"],
            title=response.get("title", ""),
            description=response.get("description"),
            duration=response.get("duration"),
            content_type=response.get("contentType"),
            media_type=response.get("mediaType"),
            genre=response.get("genre", []),
            release_date=response.get("releaseDate"),
            rating=response.get("rating"),
            language=response.get("language"),
            subtitle_languages=response.get("subtitleLanguages", []),
            poster_url=response.get("posterUrl"),
            thumbnail_url=response.get("thumbnailUrl"),
            trailer_url=response.get("trailerUrl"),
            tags=response.get("tags", []),
            external_references=response.get("externalReferences", {})
        )
    
    async def get_asset_playback_info(self, asset_id: str, user_id: Optional[str] = None) -> PlaybackInfo:
        """Récupère les informations de lecture pour un asset"""
        
        data = {}
        if user_id:
            data["userId"] = user_id
        
        response = await self._make_request(
            "POST",
            f"/customer/{self.config.customer}/businessunit/{self.config.business_unit}/entitlement/{asset_id}/play",
            data=data
        )
        
        # Trouve le format de streaming préféré
        formats = response.get("formats", [])
        preferred_format = None
        
        for format_info in formats:
            if format_info.get("format") in ["HLS", "DASH"]:
                preferred_format = format_info
                break
        
        if not preferred_format:
            raise RedBeeAPIError("Aucun format de streaming supporté trouvé")
        
        return PlaybackInfo(
            asset_id=asset_id,
            format_type=preferred_format["format"].lower(),
            media_locator=preferred_format["mediaLocator"],
            drm_license_url=preferred_format.get("drmLicenseUrl"),
            subtitle_tracks=response.get("subtitleTracks", []),
            audio_tracks=response.get("audioTracks", []),
            quality_levels=response.get("qualityLevels", []),
            expires_at=response.get("expiresAt"),
            restrictions=response.get("contractRestrictions", {})
        )
    
    # =====================================
    # User Entitlements
    # =====================================
    
    async def get_user_entitlements(self, user_id: str) -> List[UserEntitlement]:
        """Récupère les droits d'un utilisateur"""
        
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
        """Récupère les analytics d'un contenu"""
        
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
        """Récupère l'historique de visionnage d'un utilisateur"""
        
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
        """Récupère les métriques globales de la plateforme"""
        
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
        """Récupère les informations de configuration de l'unité commerciale"""
        
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