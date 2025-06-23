"""
MCP Server for Red Bee Media OTT Platform (stdio mode)
Based on Red Bee Media Exposure API
Documentation: https://exposure.api.redbee.live/docs
"""

import asyncio
import logging
from typing import List

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ServerCapabilities

from .handler import McpHandler

# Configure logging for MCP (no console output)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/redbee-mcp.log'),
    ]
)
logger = logging.getLogger(__name__)

# Global handler instance
mcp_handler = McpHandler()

# Create MCP server
server = Server("redbee-mcp")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """Handler to list available tools"""
    return await mcp_handler.list_tools()

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handler to call a tool"""
    try:
        result = await mcp_handler.call_tool(name, arguments or {})
        return result
    except Exception as e:
        logger.error(f"Error calling tool {name}: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]

async def main():
    """Main entry point for the MCP stdio server"""
    # No startup logs to avoid stdout pollution in MCP mode
    
    # Server always starts, validation happens when tools are called
    
    # Start the MCP server
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="redbee-mcp",
                server_version="1.0.0",
                capabilities=ServerCapabilities(
                    tools={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main()) 