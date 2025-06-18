#!/usr/bin/env python3
"""
Bridge MCP pour se connecter au serveur Red Bee déployé sur AWS
Usage dans mcp.json avec python bridge_aws.py
"""

import asyncio
import logging
import os
import sys
import json
from typing import List
import httpx

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ServerCapabilities
from mcp.server.stdio import stdio_server

# Configuration logging minimaliste
logging.basicConfig(level=logging.WARNING)

class AWSBridge:
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_tools(self) -> List[Tool]:
        try:
            response = await self.client.get(f"{self.server_url}/tools")
            response.raise_for_status()
            data = response.json()
            
            tools = []
            for tool_data in data["tools"]:
                tools.append(Tool(**tool_data))
            return tools
        except:
            return []
    
    async def call_tool(self, name: str, arguments: dict) -> List[TextContent]:
        try:
            payload = {"name": name, "arguments": arguments}
            response = await self.client.post(
                f"{self.server_url}/call",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            
            if result["success"]:
                return result["data"]
            else:
                return [TextContent(type="text", text=f"Erreur: {result.get('error', 'Erreur inconnue')}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Erreur de connexion: {str(e)}")]
    
    async def close(self):
        await self.client.aclose()

# Serveur MCP
app = Server("redbee-aws-bridge")
bridge = None

@app.list_tools()
async def handle_list_tools() -> List[Tool]:
    if bridge:
        return await bridge.get_tools()
    return []

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
    if bridge:
        return await bridge.call_tool(name, arguments)
    return [TextContent(type="text", text="Bridge non initialisé")]

async def main():
    global bridge
    
    # URL du serveur AWS (configurable via env ou par défaut votre IP)
    server_url = os.getenv("REDBEE_AWS_SERVER", "http://51.20.4.56:8000")
    
    bridge = AWSBridge(server_url)
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="redbee-aws-bridge",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(tools={})
                )
            )
    finally:
        if bridge:
            await bridge.close()

if __name__ == "__main__":
    asyncio.run(main()) 