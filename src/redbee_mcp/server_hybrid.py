#!/usr/bin/env python3
"""
Serveur MCP hybride pour Red Bee Media
- Interface MCP stdio native (comme les autres MCP)
- Utilise le serveur HTTP AWS en arrière-plan
"""

import asyncio
import logging
import os
from typing import Any, Dict, List
import json

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ServerCapabilities
from mcp.server.stdio import stdio_server

# Import conditionnel pour éviter l'erreur si httpx n'est pas installé
try:
    import httpx
    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False

# Configuration du logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Configuration
AWS_SERVER_URL = os.getenv("REDBEE_AWS_SERVER", "http://51.20.4.56:8000")

async def call_aws_api(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Appelle l'API AWS si disponible, sinon retourne une erreur"""
    if not HTTP_AVAILABLE:
        return {
            "success": False,
            "error": "httpx non installé - installez avec: pip install httpx"
        }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                response = await client.get(f"{AWS_SERVER_URL}{endpoint}")
            else:
                response = await client.post(
                    f"{AWS_SERVER_URL}{endpoint}",
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {
            "success": False,
            "error": f"Erreur connexion AWS: {str(e)}"
        }

# Serveur MCP
app = Server("redbee-mcp-hybrid")

@app.list_tools()
async def handle_list_tools() -> List[Tool]:
    """Liste tous les outils MCP disponibles"""
    
    # Si httpx n'est pas disponible, retourner un outil d'info
    if not HTTP_AVAILABLE:
        return [Tool(
            name="install_httpx",
            description="Installer httpx pour activer Red Bee MCP",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )]
    
    # Récupérer les outils depuis AWS
    result = await call_aws_api("/tools")
    if result.get("success"):
        tools = []
        for tool_data in result["tools"]:
            tools.append(Tool(**tool_data))
        logger.info(f"Red Bee MCP: {len(tools)} outils chargés depuis AWS")
        return tools
    else:
        # Serveur AWS indisponible, retourner un outil d'erreur
        return [Tool(
            name="aws_server_error",
            description=f"Erreur serveur AWS: {result.get('error', 'Indisponible')}",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Gestionnaire principal pour les appels d'outils MCP"""
    
    # Cas spéciaux pour les erreurs
    if name == "install_httpx":
        return [TextContent(
            type="text",
            text="Pour activer Red Bee MCP, installez httpx:\n\npip install httpx\n\nPuis redémarrez Cursor."
        )]
    
    if name == "aws_server_error":
        return [TextContent(
            type="text",
            text=f"Le serveur AWS Red Bee n'est pas accessible.\nVérifiez que le serveur tourne sur: {AWS_SERVER_URL}"
        )]
    
    # Appel normal vers AWS
    if not HTTP_AVAILABLE:
        return [TextContent(
            type="text",
            text="httpx non installé. Exécutez: pip install httpx"
        )]
    
    logger.info(f"Red Bee MCP: Appel de l'outil '{name}' avec arguments: {arguments}")
    
    result = await call_aws_api("/call", "POST", {
        "name": name,
        "arguments": arguments
    })
    
    if result.get("success"):
        return result["data"]
    else:
        return [TextContent(
            type="text",
            text=f"Erreur: {result.get('error', 'Erreur inconnue')}"
        )]

async def main():
    """Point d'entrée principal du serveur MCP hybride"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="redbee-mcp-hybrid",
                server_version="1.0.0",
                capabilities=ServerCapabilities(
                    tools={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main()) 