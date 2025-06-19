"""
Data models for Red Bee Media OTT Platform API
Based on official documentation: https://redbee.live/docs/
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field


class RedBeeConfig(BaseModel):
    """Configuration for Red Bee Media API"""
    customer: str = Field(description="Red Bee Customer ID")
    business_unit: str = Field(description="Business Unit ID")
    exposure_base_url: str = Field(description="Exposure API base URL")
    config_id: Optional[str] = Field(default=None, description="Config ID for certain endpoints (e.g., sandwich)")
    session_token: Optional[str] = Field(default=None, description="Session token for authentication")
    device_id: Optional[str] = Field(default=None, description="Device ID")
    username: Optional[str] = Field(default=None, description="Username for authentication")
    password: Optional[str] = Field(default=None, description="Password for authentication")
    timeout: int = Field(default=30, description="Request timeout in seconds")


class AuthenticationResponse(BaseModel):
    """Authentication response"""
    session_token: str = Field(description="Session token")
    device_id: str = Field(description="Device ID")
    expires_at: Optional[datetime] = Field(default=None, description="Token expiration date")


class Asset(BaseModel):
    """Red Bee Media Asset (content)"""
    asset_id: str = Field(description="Unique asset ID")
    title: str = Field(description="Content title")
    description: Optional[str] = Field(default=None, description="Content description")
    duration: Optional[int] = Field(default=None, description="Duration in seconds")
    content_type: Optional[str] = Field(default=None, description="Content type: vod, live, podcast")
    media_type: Optional[str] = Field(default=None, description="Media type")
    genre: Optional[List[str]] = Field(default=None, description="Content genres")
    release_date: Optional[datetime] = Field(default=None, description="Release date")
    rating: Optional[str] = Field(default=None, description="Content rating")
    language: Optional[str] = Field(default=None, description="Primary language")
    subtitle_languages: Optional[List[str]] = Field(default=None, description="Available subtitle languages")
    poster_url: Optional[str] = Field(default=None, description="Poster URL")
    thumbnail_url: Optional[str] = Field(default=None, description="Thumbnail URL")
    trailer_url: Optional[str] = Field(default=None, description="Trailer URL")
    tags: Optional[List[str]] = Field(default=None, description="Associated tags")
    external_references: Optional[Dict[str, str]] = Field(default=None, description="External references")


class PlaybackInfo(BaseModel):
    """Asset playback information"""
    asset_id: str = Field(description="Asset ID")
    format_type: str = Field(description="Format type: hls, dash")
    media_locator: str = Field(description="Playback manifest URL")
    drm_license_url: Optional[str] = Field(default=None, description="DRM license URL")
    subtitle_tracks: Optional[List[Dict[str, str]]] = Field(default=None, description="Subtitle tracks")
    audio_tracks: Optional[List[Dict[str, str]]] = Field(default=None, description="Audio tracks")
    quality_levels: Optional[List[Dict[str, Any]]] = Field(default=None, description="Quality levels")
    expires_at: Optional[datetime] = Field(default=None, description="Expiration date")
    restrictions: Optional[Dict[str, Any]] = Field(default=None, description="Contract restrictions")


class UserEntitlement(BaseModel):
    """User access rights"""
    user_id: str = Field(description="User ID")
    asset_id: str = Field(description="Asset ID")
    entitlement_type: str = Field(description="Entitlement type: subscription, purchase, rental")
    expires_at: Optional[datetime] = Field(default=None, description="Entitlement expiration date")
    restrictions: Optional[Dict[str, Any]] = Field(default=None, description="Applicable restrictions")


class SearchParams(BaseModel):
    """Search parameters"""
    query: Optional[str] = Field(default=None, description="Search term")
    content_type: Optional[str] = Field(default=None, description="Content type filter")
    genre: Optional[str] = Field(default=None, description="Genre filter")
    language: Optional[str] = Field(default=None, description="Language filter")
    page: int = Field(default=1, description="Page number")
    per_page: int = Field(default=20, description="Results per page")
    sort_by: Optional[str] = Field(default=None, description="Sort criteria")
    sort_order: Optional[str] = Field(default="asc", description="Sort order: asc, desc")


class SearchResult(BaseModel):
    """Search result"""
    total_results: int = Field(description="Total number of results")
    page: int = Field(description="Current page")
    per_page: int = Field(description="Results per page")
    total_pages: int = Field(description="Total number of pages")
    assets: List[Asset] = Field(description="List of found assets")


class AnalyticsEvent(BaseModel):
    """Analytics event"""
    event_type: str = Field(description="Event type")
    timestamp: datetime = Field(description="Event timestamp")
    asset_id: Optional[str] = Field(default=None, description="Related asset ID")
    user_id: Optional[str] = Field(default=None, description="User ID")
    session_id: Optional[str] = Field(default=None, description="Session ID")
    device_info: Optional[Dict[str, str]] = Field(default=None, description="Device information")
    playback_position: Optional[int] = Field(default=None, description="Playback position in seconds")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ContentAnalytics(BaseModel):
    """Content analytics"""
    asset_id: str = Field(description="Asset ID")
    period_start: datetime = Field(description="Period start")
    period_end: datetime = Field(description="Period end")
    total_views: int = Field(description="Total number of views")
    unique_viewers: int = Field(description="Number of unique viewers")
    total_watch_time: int = Field(description="Total watch time in seconds")
    average_watch_time: float = Field(description="Average watch time in seconds")
    completion_rate: float = Field(description="Completion rate as percentage")
    geographic_distribution: Optional[Dict[str, int]] = Field(default=None, description="Geographic distribution")
    device_distribution: Optional[Dict[str, int]] = Field(default=None, description="Device distribution")


class ViewingHistory(BaseModel):
    """User viewing history"""
    user_id: str = Field(description="User ID")
    asset_id: str = Field(description="Asset ID")
    started_at: datetime = Field(description="Viewing start time")
    ended_at: Optional[datetime] = Field(default=None, description="Viewing end time")
    watch_duration: int = Field(description="Watched duration in seconds")
    completion_percentage: float = Field(description="Completion percentage")
    device_type: Optional[str] = Field(default=None, description="Device type")
    quality: Optional[str] = Field(default=None, description="Streaming quality")


class ApiResponse(BaseModel):
    """Generic API response"""
    success: bool = Field(description="Success indicator")
    data: Optional[Any] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message")
    error_code: Optional[str] = Field(default=None, description="Error code")
    message: Optional[str] = Field(default=None, description="Informational message")


class PlatformMetrics(BaseModel):
    """Platform general metrics"""
    period_start: datetime = Field(description="Period start")
    period_end: datetime = Field(description="Period end")
    total_users: int = Field(description="Total number of users")
    active_users: int = Field(description="Active users")
    total_content_hours: float = Field(description="Total content hours")
    total_watch_hours: float = Field(description="Total watch hours")
    popular_content: List[Dict[str, Any]] = Field(description="Popular content")
    user_engagement: Dict[str, float] = Field(description="Engagement metrics")


class BusinessUnitInfo(BaseModel):
    """Business unit information"""
    customer: str = Field(description="Customer ID")
    business_unit: str = Field(description="Business unit ID")
    name: str = Field(description="Business unit name")
    description: Optional[str] = Field(default=None, description="Description")
    features: List[str] = Field(description="Enabled features")
    settings: Dict[str, Any] = Field(description="Configuration settings")
    locale: str = Field(description="Default locale")
    timezone: str = Field(description="Timezone") 