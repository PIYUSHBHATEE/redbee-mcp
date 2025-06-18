"""
Modèles de données pour l'API Red Bee Media OTT Platform
Basé sur la documentation officielle : https://redbee.live/docs/
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field


class RedBeeConfig(BaseModel):
    """Configuration pour l'API Red Bee Media"""
    customer: str = Field(description="Customer ID Red Bee")
    business_unit: str = Field(description="Business Unit ID")
    exposure_base_url: str = Field(description="URL de base de l'API Exposure")
    config_id: Optional[str] = Field(default=None, description="Config ID pour certains endpoints (ex: sandwich)")
    session_token: Optional[str] = Field(default=None, description="Token de session pour l'authentification")
    device_id: Optional[str] = Field(default=None, description="ID de l'appareil")
    username: Optional[str] = Field(default=None, description="Nom d'utilisateur pour l'authentification")
    password: Optional[str] = Field(default=None, description="Mot de passe pour l'authentification")
    timeout: int = Field(default=30, description="Timeout des requêtes en secondes")


class AuthenticationResponse(BaseModel):
    """Réponse d'authentification"""
    session_token: str = Field(description="Token de session")
    device_id: str = Field(description="ID de l'appareil")
    expires_at: Optional[datetime] = Field(default=None, description="Date d'expiration du token")


class Asset(BaseModel):
    """Asset (contenu) Red Bee Media"""
    asset_id: str = Field(description="ID unique de l'asset")
    title: str = Field(description="Titre du contenu")
    description: Optional[str] = Field(default=None, description="Description du contenu")
    duration: Optional[int] = Field(default=None, description="Durée en secondes")
    content_type: Optional[str] = Field(default=None, description="Type de contenu: vod, live, podcast")
    media_type: Optional[str] = Field(default=None, description="Type de média")
    genre: Optional[List[str]] = Field(default=None, description="Genres du contenu")
    release_date: Optional[datetime] = Field(default=None, description="Date de sortie")
    rating: Optional[str] = Field(default=None, description="Classification du contenu")
    language: Optional[str] = Field(default=None, description="Langue principale")
    subtitle_languages: Optional[List[str]] = Field(default=None, description="Langues des sous-titres disponibles")
    poster_url: Optional[str] = Field(default=None, description="URL de l'affiche")
    thumbnail_url: Optional[str] = Field(default=None, description="URL de la vignette")
    trailer_url: Optional[str] = Field(default=None, description="URL de la bande-annonce")
    tags: Optional[List[str]] = Field(default=None, description="Tags associés")
    external_references: Optional[Dict[str, str]] = Field(default=None, description="Références externes")


class PlaybackInfo(BaseModel):
    """Informations de lecture d'un asset"""
    asset_id: str = Field(description="ID de l'asset")
    format_type: str = Field(description="Type de format: hls, dash")
    media_locator: str = Field(description="URL du manifest de lecture")
    drm_license_url: Optional[str] = Field(default=None, description="URL de la licence DRM")
    subtitle_tracks: Optional[List[Dict[str, str]]] = Field(default=None, description="Pistes de sous-titres")
    audio_tracks: Optional[List[Dict[str, str]]] = Field(default=None, description="Pistes audio")
    quality_levels: Optional[List[Dict[str, Any]]] = Field(default=None, description="Niveaux de qualité")
    expires_at: Optional[datetime] = Field(default=None, description="Date d'expiration")
    restrictions: Optional[Dict[str, Any]] = Field(default=None, description="Restrictions de contrat")


class UserEntitlement(BaseModel):
    """Droits d'accès d'un utilisateur"""
    user_id: str = Field(description="ID de l'utilisateur")
    asset_id: str = Field(description="ID de l'asset")
    entitlement_type: str = Field(description="Type de droit: subscription, purchase, rental")
    expires_at: Optional[datetime] = Field(default=None, description="Date d'expiration du droit")
    restrictions: Optional[Dict[str, Any]] = Field(default=None, description="Restrictions applicables")


class SearchParams(BaseModel):
    """Paramètres de recherche"""
    query: Optional[str] = Field(default=None, description="Terme de recherche")
    content_type: Optional[str] = Field(default=None, description="Type de contenu à filtrer")
    genre: Optional[str] = Field(default=None, description="Genre à filtrer")
    language: Optional[str] = Field(default=None, description="Langue à filtrer")
    page: int = Field(default=1, description="Numéro de page")
    per_page: int = Field(default=20, description="Nombre de résultats par page")
    sort_by: Optional[str] = Field(default=None, description="Critère de tri")
    sort_order: Optional[str] = Field(default="asc", description="Ordre de tri: asc, desc")


class SearchResult(BaseModel):
    """Résultat de recherche"""
    total_results: int = Field(description="Nombre total de résultats")
    page: int = Field(description="Page actuelle")
    per_page: int = Field(description="Résultats par page")
    total_pages: int = Field(description="Nombre total de pages")
    assets: List[Asset] = Field(description="Liste des assets trouvés")


class AnalyticsEvent(BaseModel):
    """Événement analytics"""
    event_type: str = Field(description="Type d'événement")
    timestamp: datetime = Field(description="Horodatage de l'événement")
    asset_id: Optional[str] = Field(default=None, description="ID de l'asset concerné")
    user_id: Optional[str] = Field(default=None, description="ID de l'utilisateur")
    session_id: Optional[str] = Field(default=None, description="ID de session")
    device_info: Optional[Dict[str, str]] = Field(default=None, description="Informations sur l'appareil")
    playback_position: Optional[int] = Field(default=None, description="Position de lecture en secondes")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Métadonnées additionnelles")


class ContentAnalytics(BaseModel):
    """Analytics d'un contenu"""
    asset_id: str = Field(description="ID de l'asset")
    period_start: datetime = Field(description="Début de la période")
    period_end: datetime = Field(description="Fin de la période")
    total_views: int = Field(description="Nombre total de vues")
    unique_viewers: int = Field(description="Nombre de spectateurs uniques")
    total_watch_time: int = Field(description="Temps de visionnage total en secondes")
    average_watch_time: float = Field(description="Temps de visionnage moyen en secondes")
    completion_rate: float = Field(description="Taux de complétion en pourcentage")
    geographic_distribution: Optional[Dict[str, int]] = Field(default=None, description="Distribution géographique")
    device_distribution: Optional[Dict[str, int]] = Field(default=None, description="Distribution par appareil")


class ViewingHistory(BaseModel):
    """Historique de visionnage d'un utilisateur"""
    user_id: str = Field(description="ID de l'utilisateur")
    asset_id: str = Field(description="ID de l'asset")
    started_at: datetime = Field(description="Début du visionnage")
    ended_at: Optional[datetime] = Field(default=None, description="Fin du visionnage")
    watch_duration: int = Field(description="Durée regardée en secondes")
    completion_percentage: float = Field(description="Pourcentage de complétion")
    device_type: Optional[str] = Field(default=None, description="Type d'appareil")
    quality: Optional[str] = Field(default=None, description="Qualité de diffusion")


class ApiResponse(BaseModel):
    """Réponse générique de l'API"""
    success: bool = Field(description="Indicateur de succès")
    data: Optional[Any] = Field(default=None, description="Données de réponse")
    error: Optional[str] = Field(default=None, description="Message d'erreur")
    error_code: Optional[str] = Field(default=None, description="Code d'erreur")
    message: Optional[str] = Field(default=None, description="Message informatif")


class PlatformMetrics(BaseModel):
    """Métriques générales de la plateforme"""
    period_start: datetime = Field(description="Début de la période")
    period_end: datetime = Field(description="Fin de la période")
    total_users: int = Field(description="Nombre total d'utilisateurs")
    active_users: int = Field(description="Utilisateurs actifs")
    total_content_hours: float = Field(description="Heures de contenu total")
    total_watch_hours: float = Field(description="Heures de visionnage total")
    popular_content: List[Dict[str, Any]] = Field(description="Contenu populaire")
    user_engagement: Dict[str, float] = Field(description="Métriques d'engagement")


class BusinessUnitInfo(BaseModel):
    """Informations sur l'unité commerciale"""
    customer: str = Field(description="ID du customer")
    business_unit: str = Field(description="ID de l'unité commerciale")
    name: str = Field(description="Nom de l'unité commerciale")
    description: Optional[str] = Field(default=None, description="Description")
    features: List[str] = Field(description="Fonctionnalités activées")
    settings: Dict[str, Any] = Field(description="Paramètres de configuration")
    locale: str = Field(description="Locale par défaut")
    timezone: str = Field(description="Fuseau horaire") 