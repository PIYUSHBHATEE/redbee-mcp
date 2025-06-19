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
    """Récupère tous les achats d'un compte utilisateur"""
    
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
                text=f"Achats du compte Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur récupération achats Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la récupération des achats: {str(e)}"
        )]


async def get_account_transactions(
    config: RedBeeConfig,
    sessionToken: str
) -> List[TextContent]:
    """Récupère l'historique des transactions d'un compte"""
    
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
                text=f"Transactions du compte Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur récupération transactions Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la récupération des transactions: {str(e)}"
        )]


async def get_offerings(
    config: RedBeeConfig,
    sessionToken: Optional[str] = None
) -> List[TextContent]:
    """Récupère toutes les offres disponibles"""
    
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
                text=f"Offres disponibles Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur récupération offres Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la récupération des offres: {str(e)}"
        )]


async def purchase_product_offering(
    config: RedBeeConfig,
    sessionToken: str,
    offeringId: str,
    paymentMethod: Optional[str] = None
) -> List[TextContent]:
    """Achète une offre de produit"""
    
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
                text=f"Achat effectué Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur achat Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de l'achat: {str(e)}"
        )]


async def cancel_purchase_subscription(
    config: RedBeeConfig,
    sessionToken: str,
    purchaseId: str
) -> List[TextContent]:
    """Annule un abonnement acheté"""
    
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
                text=f"Annulation abonnement Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur annulation Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de l'annulation: {str(e)}"
        )]


async def get_stored_payment_methods(
    config: RedBeeConfig,
    sessionToken: str
) -> List[TextContent]:
    """Récupère les méthodes de paiement enregistrées"""
    
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
                text=f"Méthodes de paiement Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur récupération méthodes paiement Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de la récupération des méthodes de paiement: {str(e)}"
        )]


async def add_payment_method(
    config: RedBeeConfig,
    sessionToken: str,
    paymentMethodData: Dict[str, Any]
) -> List[TextContent]:
    """Ajoute une nouvelle méthode de paiement"""
    
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
                text=f"Méthode de paiement ajoutée Red Bee Media:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
            )]
            
    except RedBeeAPIError as e:
        return [TextContent(
            type="text",
            text=f"Erreur ajout méthode paiement Red Bee: {e.message} (Status: {e.status_code})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erreur lors de l'ajout de la méthode de paiement: {str(e)}"
        )]


# MCP Tool definitions
PURCHASES_TOOLS = [
    Tool(
        name="get_account_purchases",
        description="Récupère tous les achats d'un compte utilisateur",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "Token de session utilisateur"
                },
                "includeExpired": {
                    "type": "boolean",
                    "description": "Inclure les achats expirés",
                    "default": False
                }
            },
            "required": ["sessionToken"]
        }
    ),
    Tool(
        name="get_account_transactions",
        description="Récupère l'historique des transactions d'un compte",
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
        name="get_offerings",
        description="Récupère toutes les offres disponibles",
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
        name="purchase_product_offering",
        description="Achète une offre de produit",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "Token de session utilisateur"
                },
                "offeringId": {
                    "type": "string",
                    "description": "ID de l'offre à acheter"
                },
                "paymentMethod": {
                    "type": "string",
                    "description": "Méthode de paiement (optionnel)"
                }
            },
            "required": ["sessionToken", "offeringId"]
        }
    ),
    Tool(
        name="cancel_purchase_subscription",
        description="Annule un abonnement acheté",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "Token de session utilisateur"
                },
                "purchaseId": {
                    "type": "string",
                    "description": "ID de l'achat à annuler"
                }
            },
            "required": ["sessionToken", "purchaseId"]
        }
    ),
    Tool(
        name="get_stored_payment_methods",
        description="Récupère les méthodes de paiement enregistrées",
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
        name="add_payment_method",
        description="Ajoute une nouvelle méthode de paiement",
        inputSchema={
            "type": "object",
            "properties": {
                "sessionToken": {
                    "type": "string",
                    "description": "Token de session utilisateur"
                },
                "paymentMethodData": {
                    "type": "object",
                    "description": "Données de la méthode de paiement"
                }
            },
            "required": ["sessionToken", "paymentMethodData"]
        }
    )
] 

def get_all_purchase_tools() -> List[Tool]:
    """Return all purchase tools"""
    return PURCHASES_TOOLS 