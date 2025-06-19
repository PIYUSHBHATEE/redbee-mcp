"""
MCP Tools for Red Bee Media Purchases and Transactions

This module provides purchase and transaction management tools for Red Bee Media platform.
"""

import json
from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent

from ..client import RedBeeClient, RedBeeAPIError
from ..models import RedBeeConfig


async def get_account_purchases(
    config: RedBeeConfig,
    sessionToken: str,
    includeExpired: Optional[bool] = False
) -> List[TextContent]:
    """Retrieves all purchases for a user account"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = sessionToken
            
            params = {
                "includeExpired": includeExpired
            }
            
            result = await client._make_request(
                "GET",
                f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/store/purchases",
                params=params,
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media Account Purchases:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee purchases retrieval error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during purchases retrieval: {str(e)}"
        )]


async def get_account_transactions(
    config: RedBeeConfig,
    sessionToken: str
) -> List[TextContent]:
    """Retrieves transaction history for an account"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = sessionToken
            
            result = await client._make_request(
                "GET",
                f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/store/transactions",
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media Account Transactions:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee transactions retrieval error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during transactions retrieval: {str(e)}"
        )]


async def get_offerings(
    config: RedBeeConfig,
    sessionToken: Optional[str] = None
) -> List[TextContent]:
    """Retrieves all available offerings"""
    
    try:
        async with RedBeeClient(config) as client:
            if sessionToken:
                client.session_token = sessionToken
            elif not client.session_token:
                await client.authenticate_anonymous()
            
            result = await client._make_request(
                "GET",
                f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/store/offerings",
                include_auth=bool(sessionToken)
            )
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media Available Offerings:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee offerings retrieval error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during offerings retrieval: {str(e)}"
        )]


async def purchase_product_offering(
    config: RedBeeConfig,
    sessionToken: str,
    offeringId: str,
    paymentMethod: Optional[str] = None
) -> List[TextContent]:
    """Purchases a product offering"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = sessionToken
            
            purchase_data = {
                "offeringId": offeringId
            }
            
            if paymentMethod:
                purchase_data["paymentMethod"] = paymentMethod
            
            result = await client._make_request(
                "POST",
                f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/store/purchase",
                data=purchase_data,
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media Purchase Completed:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee purchase error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during purchase: {str(e)}"
        )]


async def cancel_purchase_subscription(
    config: RedBeeConfig,
    sessionToken: str,
    purchaseId: str
) -> List[TextContent]:
    """Cancels a purchased subscription"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = sessionToken
            
            result = await client._make_request(
                "DELETE",
                f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/store/purchases/{purchaseId}",
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media Subscription Cancellation:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee cancellation error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during cancellation: {str(e)}"
        )]


async def get_stored_payment_methods(
    config: RedBeeConfig,
    sessionToken: str
) -> List[TextContent]:
    """Retrieves stored payment methods"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = sessionToken
            
            result = await client._make_request(
                "GET",
                f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/store/payment/methods",
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media Payment Methods:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee payment methods retrieval error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during payment methods retrieval: {str(e)}"
        )]


async def add_payment_method(
    config: RedBeeConfig,
    sessionToken: str,
    paymentMethodData: Dict[str, Any]
) -> List[TextContent]:
    """Adds a new payment method"""
    
    try:
        async with RedBeeClient(config) as client:
            client.session_token = sessionToken
            
            result = await client._make_request(
                "POST",
                f"/v2/customer/{config.customer}/businessunit/{config.business_unit}/store/payment/methods",
                data=paymentMethodData,
                include_auth=True
            )
            
            return [TextContent(
                type="text",
                text=f"Red Bee Media Payment Method Added:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Red Bee payment method addition error: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error during payment method addition: {str(e)}"
        )]


# MCP Tool definitions
PURCHASES_TOOLS = [
    Tool(
        name="get_account_purchases",
        description="Retrieves all purchases for a user account",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "User session token"
                },
                "includeExpired": {
                    "type": "boolean",
                    "description": "Include expired purchases",
                    "default": False
                }
            },
            "required": ["sessionToken"]
        }
    ),
    Tool(
        name="get_account_transactions",
        description="Retrieves transaction history for an account",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "User session token"
                }
            },
            "required": ["sessionToken"]
        }
    ),
    Tool(
        name="get_offerings",
        description="Retrieves all available offerings",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "User session token (optional)"
                }
            },
            "required": []
        }
    ),
    Tool(
        name="purchase_product_offering",
        description="Purchases a product offering",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "User session token"
                },
                "offeringId": {
                    "type": "string",
                    "description": "Offering ID to purchase"
                },
                "paymentMethod": {
                    "type": "string",
                    "description": "Payment method (optional)"
                }
            },
            "required": ["sessionToken", "offeringId"]
        }
    ),
    Tool(
        name="cancel_purchase_subscription",
        description="Cancels a purchased subscription",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "User session token"
                },
                "purchaseId": {
                    "type": "string",
                    "description": "Purchase ID to cancel"
                }
            },
            "required": ["sessionToken", "purchaseId"]
        }
    ),
    Tool(
        name="get_stored_payment_methods",
        description="Retrieves stored payment methods",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "User session token"
                }
            },
            "required": ["sessionToken"]
        }
    ),
    Tool(
        name="add_payment_method",
        description="Adds a new payment method",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "User session token"
                },
                "paymentMethodData": {
                    "type": "object",
                    "description": "Payment method data"
                }
            },
            "required": ["sessionToken", "paymentMethodData"]
        }
    )
] 

def get_all_purchase_tools() -> List[Tool]:
    """Return all purchase tools"""
    return PURCHASES_TOOLS 