#!/usr/bin/env python3
"""
CLI entry point for Red Bee MCP
Usage: redbee-mcp --server-url http://server:8000 --stdio
"""

import argparse
import asyncio
import logging
import os
import signal
import sys
from typing import List, Optional, Dict, Any
import click
import json

# Conditional import to avoid error if httpx is not installed
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

# Configure logging to file to avoid polluting stdout in MCP mode
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/redbee-mcp.log'),
    ]
)
logger = logging.getLogger(__name__)

class RedBeeMCPCLI:
    def __init__(self):
        self.config = None
        self.client = None
        self.server = None

    def parse_args(self) -> argparse.Namespace:
        """Parse command line arguments and environment variables."""
        parser = argparse.ArgumentParser(
            description="Red Bee MCP Server - MCP interface for Red Bee Media APIs"
        )
        
        # Required arguments
        parser.add_argument(
            "--customer", 
            default=os.getenv("REDBEE_CUSTOMER"),
            help="Red Bee customer identifier"
        )
        parser.add_argument(
            "--business-unit", 
            default=os.getenv("REDBEE_BUSINESS_UNIT"),
            help="Red Bee business unit identifier"
        )
        
        # Optional arguments
        parser.add_argument(
            "--exposure-base-url", 
            default=os.getenv("REDBEE_EXPOSURE_BASE_URL", "https://exposure.api.redbee.live"),
            help="Red Bee Exposure API base URL"
        )
        parser.add_argument(
            "--username", 
            default=os.getenv("REDBEE_USERNAME"),
            help="Username for authentication (optional)"
        )
        parser.add_argument(
            "--session-token", 
            default=os.getenv("REDBEE_SESSION_TOKEN"),
            help="Session token for authentication (optional)"
        )
        parser.add_argument(
            "--device-id", 
            default=os.getenv("REDBEE_DEVICE_ID"),
            help="Device ID for the session (optional)"
        )
        parser.add_argument(
            "--config-id", 
            default=os.getenv("REDBEE_CONFIG_ID"),
            help="Configuration ID (optional)"
        )
        
        return parser.parse_args()

    def create_config(self, args: argparse.Namespace):
        """Create RedBeeConfig from parsed arguments."""
        from .models import RedBeeConfig
        
        return RedBeeConfig(
            customer=args.customer or "demo",
            business_unit=args.business_unit or "demo", 
            exposure_base_url=args.exposure_base_url,
            username=args.username,
            session_token=args.session_token,
            device_id=args.device_id,
            config_id=args.config_id
        )

    def setup_client_and_server(self) -> None:
        """Initialize client and create MCP server with tools."""
        from .client import RedBeeClient
        from .tools.auth import get_all_auth_tools
        from .tools.content import get_all_content_tools  
        from .tools.user_management import get_all_user_management_tools
        from .tools.purchases import get_all_purchase_tools
        from .tools.system import get_all_system_tools
        
        self.client = RedBeeClient(self.config)
        
        # Get all tools from different modules
        tools = []
        tools.extend(get_all_auth_tools())
        tools.extend(get_all_content_tools())  
        tools.extend(get_all_user_management_tools())
        tools.extend(get_all_purchase_tools())
        tools.extend(get_all_system_tools())
        
        logger.info(f"Red Bee MCP: Loaded {len(tools)} tools")
        
        # The MCP server will be created in run_stdio_server directly

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down...")
        sys.exit(0)

    async def run_stdio_server(self) -> None:
        """Run the MCP server in stdio mode."""
        import mcp.server.stdio
        from .server import main as server_main
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Use the server's main function directly
            await server_main()
        except Exception as e:
            logger.error(f"Error running server: {e}")
            raise

    async def run(self) -> None:
        """Main entry point."""
        try:
            args = self.parse_args()
            self.config = self.create_config(args)
            
            # Set environment variables for the server
            os.environ["REDBEE_CUSTOMER"] = self.config.customer
            os.environ["REDBEE_BUSINESS_UNIT"] = self.config.business_unit
            os.environ["REDBEE_EXPOSURE_BASE_URL"] = self.config.exposure_base_url
            if self.config.username:
                os.environ["REDBEE_USERNAME"] = self.config.username
            if self.config.session_token:
                os.environ["REDBEE_SESSION_TOKEN"] = self.config.session_token
            if self.config.device_id:
                os.environ["REDBEE_DEVICE_ID"] = self.config.device_id
            if self.config.config_id:
                os.environ["REDBEE_CONFIG_ID"] = self.config.config_id
                
            await self.run_stdio_server()
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            raise

def main():
    """Main entry point for the CLI."""
    try:
        cli = RedBeeMCPCLI()
        
        # Check if arguments were provided
        args = sys.argv[1:]
        if not args:
            # Show help if no options are specified
            parser = argparse.ArgumentParser(
                description="Red Bee MCP Server - MCP interface for Red Bee Media APIs"
            )
            parser.add_argument("--customer", help="Red Bee customer identifier")
            parser.add_argument("--business-unit", help="Red Bee business unit identifier")
            parser.print_help()
            return
            
        asyncio.run(cli.run())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 