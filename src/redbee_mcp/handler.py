"""
Main handler for MCP requests
Extracts business logic to enable reuse in both stdio and HTTP modes
"""

import logging
import os
from typing import Any, Dict, List, Optional

from mcp.types import Tool, TextContent

from .models import RedBeeConfig
from .tools.content import CONTENT_TOOLS, search_content_v2, get_asset_details, get_playback_info, search_assets_autocomplete, get_epg_for_channel, get_episodes_for_season, get_public_asset_details, get_assets_by_tag, list_assets, search_multi_v3, get_asset_collection_entries, get_asset_thumbnail, get_seasons_for_series
from .tools.auth import AUTH_TOOLS, login_user, create_anonymous_session, validate_session_token, logout_user
from .tools.user_management import USER_MANAGEMENT_TOOLS, signup_user, change_user_password, get_user_profiles, add_user_profile, select_user_profile, get_user_preferences, set_user_preferences
from .tools.purchases import PURCHASES_TOOLS, get_account_purchases, get_account_transactions, get_offerings, purchase_product_offering, cancel_purchase_subscription, get_stored_payment_methods, add_payment_method
from .tools.system import SYSTEM_TOOLS, get_system_config_impl, get_system_time_impl, get_user_location_impl, get_active_channels_impl, get_user_devices_impl, delete_user_device_impl

logger = logging.getLogger(__name__)

class McpHandler:
    """
    Main handler for all MCP requests
    Can be used in both stdio and HTTP modes
    """
    
    def __init__(self, config: Optional[RedBeeConfig] = None):
        self.config = config or self._get_config_from_env()
    
    def _get_config_from_env(self) -> RedBeeConfig:
        """Retrieves configuration from environment variables"""
        return RedBeeConfig(
            customer=os.getenv("REDBEE_CUSTOMER", ""),
            business_unit=os.getenv("REDBEE_BUSINESS_UNIT", ""),
            exposure_base_url=os.getenv("REDBEE_EXPOSURE_BASE_URL", "https://exposure.api.redbee.live"),
            config_id=os.getenv("REDBEE_CONFIG_ID", "sandwich"),
            username=os.getenv("REDBEE_USERNAME"),
            password=os.getenv("REDBEE_PASSWORD"),
            session_token=os.getenv("REDBEE_SESSION_TOKEN"),
            device_id=os.getenv("REDBEE_DEVICE_ID"),
            timeout=int(os.getenv("REDBEE_TIMEOUT", "30"))
        )
    
    async def list_tools(self) -> List[Tool]:
        """Lists all available MCP tools for Red Bee Media"""
        tools = []
        
        # Add all tools from different modules
        tools.extend(AUTH_TOOLS)
        tools.extend(CONTENT_TOOLS)
        tools.extend(USER_MANAGEMENT_TOOLS)
        tools.extend(PURCHASES_TOOLS)
        tools.extend(SYSTEM_TOOLS)
        
        logger.info(f"Red Bee MCP: {len(tools)} available tools")
        return tools
    
    async def call_tool(self, name: str, arguments: dict) -> List[TextContent]:
        """Main handler for MCP tool calls"""
        
        # Minimal configuration validation only when calling a tool
        if not self.config.customer or not self.config.business_unit:
            return [TextContent(
                type="text",
                text="❌ Missing configuration: REDBEE_CUSTOMER and REDBEE_BUSINESS_UNIT are required.\n\nPlease configure:\n- REDBEE_CUSTOMER (e.g., CUSTOMER_NAME)\n- REDBEE_BUSINESS_UNIT (e.g., BUSINESS_UNIT_NAME)\n\nIn your mcp.json or as environment variables."
            )]
        
        try:
            logger.info(f"Red Bee MCP: Calling tool '{name}' with arguments: {arguments}")
            
            # === AUTHENTICATION TOOLS ===
            if name == "login_user":
                return await login_user(
                    config=self.config,
                    username=arguments["username"],
                    password=arguments["password"],
                    remember_me=arguments.get("remember_me", False)
                )
            
            elif name == "create_anonymous_session":
                return await create_anonymous_session(config=self.config)
            
            elif name == "validate_session_token":
                return await validate_session_token(
                    config=self.config,
                    session_token=arguments["session_token"]
                )
            
            elif name == "logout_user":
                return await logout_user(
                    config=self.config,
                    session_token=arguments["session_token"]
                )
            
            # === CONTENT TOOLS ===
            elif name == "search_content_v2":
                return await search_content_v2(
                    config=self.config,
                    query=arguments["query"],
                    locale=arguments.get("locale"),
                    types=arguments.get("types", "MOVIE,TV_SHOW"),
                    tags=arguments.get("tags"),
                    durationLower=arguments.get("durationLower"),
                    durationUpper=arguments.get("durationUpper"),
                    subtitles=arguments.get("subtitles"),
                    schemes=arguments.get("schemes"),
                    parentalRatings=arguments.get("parentalRatings"),
                    onlyPublished=arguments.get("onlyPublished", True),
                    allowedCountry=arguments.get("allowedCountry"),
                    onlyDownloadable=arguments.get("onlyDownloadable"),
                    pageSize=arguments.get("pageSize", 50),
                    pageNumber=arguments.get("pageNumber", 1),
                    service=arguments.get("service"),
                    fieldSet=arguments.get("fieldSet", "ALL"),
                    includeFields=arguments.get("includeFields"),
                    excludeFields=arguments.get("excludeFields")
                )
            
            elif name == "get_asset_details":
                return await get_asset_details(
                    config=self.config,
                    assetId=arguments["assetId"],
                    includeUserData=arguments.get("includeUserData", True)
                )
            
            elif name == "get_playback_info":
                return await get_playback_info(
                    config=self.config,
                    assetId=arguments["assetId"],
                    sessionToken=arguments["sessionToken"]
                )
            
            elif name == "search_assets_autocomplete":
                return await search_assets_autocomplete(
                    config=self.config,
                    query=arguments["query"],
                    fieldSet=arguments.get("fieldSet", "ALL")
                )
            
            elif name == "get_epg_for_channel":
                return await get_epg_for_channel(
                    config=self.config,
                    channelId=arguments["channelId"],
                    fromDate=arguments.get("fromDate"),
                    toDate=arguments.get("toDate"),
                    includeUserData=arguments.get("includeUserData", True)
                )
            
            elif name == "get_episodes_for_season":
                return await get_episodes_for_season(
                    config=self.config,
                    seasonId=arguments["seasonId"],
                    includeUserData=arguments.get("includeUserData", True)
                )
            
            elif name == "get_public_asset_details":
                return await get_public_asset_details(
                    config=self.config,
                    assetId=arguments["assetId"],
                    onlyPublished=arguments.get("onlyPublished", True),
                    fieldSet=arguments.get("fieldSet", "ALL")
                )
            
            elif name == "get_assets_by_tag":
                args = arguments or {}
                return await get_assets_by_tag(
                    self.config,
                    tagType=args.get("tagType"),
                    assetType=args.get("assetType", "MOVIE"),
                    onlyPublished=args.get("onlyPublished", True)
                )
            
            elif name == "list_assets":
                args = arguments or {}
                return await list_assets(
                    self.config,
                    assetType=args.get("assetType"),
                    assetTypes=args.get("assetTypes"),
                    pageNumber=args.get("pageNumber", 1),
                    pageSize=args.get("pageSize", 50),
                    sort=args.get("sort")
                )
            
            elif name == "search_multi_v3":
                return await search_multi_v3(
                    config=self.config,
                    query=arguments["query"],
                    types=arguments.get("types", "MOVIE,TV_SHOW"),
                    locales=arguments.get("locales"),
                    tags=arguments.get("tags"),
                    schemes=arguments.get("schemes"),
                    parentalRatings=arguments.get("parentalRatings"),
                    pageSize=arguments.get("pageSize", 50),
                    pageNumber=arguments.get("pageNumber", 1),
                    onlyPublished=arguments.get("onlyPublished", True)
                )
            
            elif name == "get_asset_collection_entries":
                return await get_asset_collection_entries(
                    config=self.config,
                    assetId=arguments["assetId"],
                    pageSize=arguments.get("pageSize", 50),
                    pageNumber=arguments.get("pageNumber", 1),
                    onlyPublished=arguments.get("onlyPublished", True),
                    fieldSet=arguments.get("fieldSet", "ALL")
                )
            
            elif name == "get_asset_thumbnail":
                return await get_asset_thumbnail(
                    config=self.config,
                    assetId=arguments["assetId"],
                    time=arguments.get("time")
                )
            
            elif name == "get_seasons_for_series":
                return await get_seasons_for_series(
                    config=self.config,
                    assetId=arguments["assetId"],
                    pageSize=arguments.get("pageSize", 50),
                    pageNumber=arguments.get("pageNumber", 1),
                    onlyPublished=arguments.get("onlyPublished", True),
                    fieldSet=arguments.get("fieldSet", "ALL")
                )
            
            # === USER MANAGEMENT TOOLS ===
            elif name == "signup_user":
                return await signup_user(
                    config=self.config,
                    username=arguments["username"],
                    password=arguments["password"],
                    email=arguments.get("email"),
                    firstName=arguments.get("firstName"),
                    lastName=arguments.get("lastName"),
                    dateOfBirth=arguments.get("dateOfBirth")
                )
            
            elif name == "change_user_password":
                return await change_user_password(
                    config=self.config,
                    sessionToken=arguments["sessionToken"],
                    oldPassword=arguments["oldPassword"],
                    newPassword=arguments["newPassword"]
                )
            
            elif name == "get_user_profiles":
                return await get_user_profiles(
                    config=self.config,
                    sessionToken=arguments["sessionToken"]
                )
            
            elif name == "add_user_profile":
                return await add_user_profile(
                    config=self.config,
                    sessionToken=arguments["sessionToken"],
                    profileName=arguments["profileName"],
                    dateOfBirth=arguments.get("dateOfBirth"),
                    avatar=arguments.get("avatar")
                )
            
            elif name == "select_user_profile":
                return await select_user_profile(
                    config=self.config,
                    sessionToken=arguments["sessionToken"],
                    profileId=arguments["profileId"]
                )
            
            elif name == "get_user_preferences":
                return await get_user_preferences(
                    config=self.config,
                    sessionToken=arguments["sessionToken"]
                )
            
            elif name == "set_user_preferences":
                return await set_user_preferences(
                    config=self.config,
                    sessionToken=arguments["sessionToken"],
                    preferences=arguments["preferences"]
                )
            
            # === PURCHASE TOOLS ===
            elif name == "get_account_purchases":
                return await get_account_purchases(
                    config=self.config,
                    sessionToken=arguments["sessionToken"],
                    includeExpired=arguments.get("includeExpired", False)
                )
            
            elif name == "get_account_transactions":
                return await get_account_transactions(
                    config=self.config,
                    sessionToken=arguments["sessionToken"]
                )
            
            elif name == "get_offerings":
                return await get_offerings(
                    config=self.config,
                    sessionToken=arguments.get("sessionToken")
                )
            
            elif name == "purchase_product_offering":
                return await purchase_product_offering(
                    config=self.config,
                    sessionToken=arguments["sessionToken"],
                    offeringId=arguments["offeringId"],
                    paymentMethod=arguments.get("paymentMethod")
                )
            
            elif name == "cancel_purchase_subscription":
                return await cancel_purchase_subscription(
                    config=self.config,
                    sessionToken=arguments["sessionToken"],
                    purchaseId=arguments["purchaseId"]
                )
            
            elif name == "get_stored_payment_methods":
                return await get_stored_payment_methods(
                    config=self.config,
                    sessionToken=arguments["sessionToken"]
                )
            
            elif name == "add_payment_method":
                return await add_payment_method(
                    config=self.config,
                    sessionToken=arguments["sessionToken"],
                    paymentMethodData=arguments["paymentMethodData"]
                )
            
            # === SYSTEM TOOLS ===
            elif name == "get_system_config":
                return await get_system_config_impl(config=self.config)
            
            elif name == "get_system_time":
                return await get_system_time_impl(config=self.config)
            
            elif name == "get_user_location":
                return await get_user_location_impl(config=self.config)
            
            elif name == "get_active_channels":
                return await get_active_channels_impl(
                    config=self.config,
                    session_token=arguments.get("sessionToken")
                )
            
            elif name == "get_user_devices":
                return await get_user_devices_impl(
                    config=self.config,
                    session_token=arguments["sessionToken"]
                )
            
            elif name == "delete_user_device":
                return await delete_user_device_impl(
                    config=self.config,
                    device_id=arguments["deviceId"],
                    session_token=arguments["sessionToken"]
                )
            
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]
                
        except Exception as e:
            logger.error(f"Error executing tool {name}: {str(e)}")
            return [TextContent(
                type="text",
                text=f"Error executing tool {name}: {str(e)}"
            )] 