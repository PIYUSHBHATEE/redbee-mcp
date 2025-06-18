#!/usr/bin/env python3
"""
CLI entry point for Red Bee MCP
Usage: redbee-mcp --server-url http://server:8000 --stdio
"""

import asyncio
import logging
import os
import sys
from typing import List, Optional
import click

# Import conditionnel pour éviter l'erreur si httpx n'est pas installé
try:
    import httpx
    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False

try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.types import Tool, TextContent, ServerCapabilities
    from mcp.server.stdio import stdio_server
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

# Configuration logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class RedBeeRemoteClient:
    """Client pour se connecter au serveur Red Bee MCP distant"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip('/')
        if HTTP_AVAILABLE:
            self.client = httpx.AsyncClient(timeout=30.0)
        else:
            self.client = None
    
    async def get_tools(self) -> List[Tool]:
        """Récupère la liste des outils depuis le serveur distant"""
        if not HTTP_AVAILABLE or not self.client:
            return [Tool(
                name="install_httpx",
                description="Install httpx dependency for Red Bee MCP",
                inputSchema={"type": "object", "properties": {}, "required": []}
            )]
        
        try:
            response = await self.client.get(f"{self.server_url}/tools")
            response.raise_for_status()
            data = response.json()
            
            tools = []
            for tool_data in data["tools"]:
                tools.append(Tool(**tool_data))
            
            logger.info(f"Red Bee MCP: Loaded {len(tools)} tools from {self.server_url}")
            return tools
            
        except Exception as e:
            return [Tool(
                name="connection_error",
                description=f"Failed to connect to Red Bee server: {str(e)}",
                inputSchema={"type": "object", "properties": {}, "required": []}
            )]
    
    async def call_tool(self, name: str, arguments: dict) -> List[TextContent]:
        """Appelle un outil via le serveur distant"""
        
        if name == "install_httpx":
            return [TextContent(
                type="text",
                text="To use Red Bee MCP, install httpx:\n\npip install httpx\n\nThen restart your MCP client."
            )]
        
        if name == "connection_error":
            return [TextContent(
                type="text",
                text=f"""Failed to connect to Red Bee MCP server.

Server URL: {self.server_url}

Please check:
1. The server is running on AWS EC2
2. The URL is correct
3. Port 8000 is accessible
4. Your internet connection

Test with: curl {self.server_url}/health"""
            )]
        
        if not HTTP_AVAILABLE or not self.client:
            return [TextContent(
                type="text",
                text="Missing dependencies. Install with: pip install httpx"
            )]
        
        try:
            payload = {"name": name, "arguments": arguments}
            response = await self.client.post(
                f"{self.server_url}/call",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                return result["data"]
            else:
                return [TextContent(
                    type="text",
                    text=f"Server error: {result.get('error', 'Unknown error')}"
                )]
                
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Communication error with AWS server: {str(e)}"
            )]
    
    async def close(self):
        """Ferme les connexions"""
        if self.client:
            await self.client.aclose()

async def run_mcp_server(server_url: str):
    """Lance le serveur MCP avec connexion au serveur distant"""
    
    if not MCP_AVAILABLE:
        click.echo("Error: MCP SDK not available. Install with: pip install mcp", err=True)
        sys.exit(1)
    
    # Créer le serveur MCP
    app = Server("redbee-mcp-client")
    client = RedBeeRemoteClient(server_url)
    
    @app.list_tools()
    async def handle_list_tools() -> List[Tool]:
        """Liste tous les outils via le serveur distant"""
        return await client.get_tools()
    
    @app.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
        """Appelle un outil via le serveur distant"""
        return await client.call_tool(name, arguments)
    
    try:
        # Démarrer le serveur MCP stdio
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="redbee-mcp-client",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(tools={})
                )
            )
    finally:
        await client.close()

@click.command()
@click.option(
    '--server-url',
    default='http://51.20.4.56:8000',
    help='Red Bee MCP server URL (default: http://51.20.4.56:8000)',
    envvar='REDBEE_SERVER_URL'
)
@click.option(
    '--stdio',
    is_flag=True,
    help='Use stdio transport (required for MCP clients like Cursor)'
)
@click.option(
    '--test',
    is_flag=True,
    help='Test connection to the server'
)
@click.version_option(version="1.0.0", prog_name="redbee-mcp")
def main(server_url: str, stdio: bool, test: bool):
    """
    Red Bee MCP Client - Connect to Red Bee Media OTT Platform via MCP
    
    Examples:
      redbee-mcp --stdio
      redbee-mcp --server-url http://your-server:8000 --stdio
      redbee-mcp --test
    """
    
    if test:
        # Test de connexion simple
        click.echo(f"Testing connection to {server_url}...")
        if HTTP_AVAILABLE:
            import httpx
            try:
                response = httpx.get(f"{server_url}/health", timeout=10)
                response.raise_for_status()
                data = response.json()
                click.echo(f"✅ Server is healthy: {data.get('status', 'unknown')}")
                sys.exit(0)
            except Exception as e:
                click.echo(f"❌ Connection failed: {e}")
                sys.exit(1)
        else:
            click.echo("❌ httpx not installed. Install with: pip install httpx")
            sys.exit(1)
    
    if stdio:
        # Lancer le serveur MCP stdio
        asyncio.run(run_mcp_server(server_url))
    else:
        # Afficher l'aide si aucune option n'est spécifiée
        click.echo("Red Bee MCP Client")
        click.echo(f"Server URL: {server_url}")
        click.echo("")
        click.echo("Use --stdio to start MCP server mode")
        click.echo("Use --test to test server connection")
        click.echo("Use --help for more options")

if __name__ == "__main__":
    main() 