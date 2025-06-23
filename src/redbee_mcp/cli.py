#!/usr/bin/env python3
"""
Enhanced CLI for Red Bee MCP
Supports modes: stdio, http, both
Usage: 
  redbee-mcp --stdio                    # Stdio mode only
  redbee-mcp --http                     # HTTP mode only  
  redbee-mcp --both                     # Both modes in parallel
  redbee-mcp --http --port 8001         # HTTP on custom port
"""

import argparse
import asyncio
import logging
import os
import signal
import sys
from typing import Optional
import multiprocessing as mp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/redbee-mcp.log'),
    ]
)
logger = logging.getLogger(__name__)

class RedBeeMCPCLI:
    """CLI for Red Bee MCP with multi-mode support"""
    
    def __init__(self):
        self.config = None

    def parse_args(self) -> argparse.Namespace:
        """Parse command line arguments and environment variables."""
        parser = argparse.ArgumentParser(
            description="Red Bee MCP Server - MCP interface for Red Bee Media APIs",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Usage examples:
  %(prog)s --stdio                    # Stdio mode only (for local AI agents)
  %(prog)s --http                     # HTTP mode only (for website)
  %(prog)s --both                     # Both modes in parallel
  %(prog)s --http --port 8001         # HTTP on custom port
  %(prog)s --http --host 127.0.0.1    # HTTP on custom host
            """
        )
        
        # Operating mode
        mode_group = parser.add_mutually_exclusive_group(required=True)
        mode_group.add_argument(
            "--stdio", 
            action="store_true",
            help="Stdio mode for local AI agents (standard MCP)"
        )
        mode_group.add_argument(
            "--http", 
            action="store_true",
            help="HTTP/SSE mode for website"
        )
        mode_group.add_argument(
            "--both", 
            action="store_true",
            help="Both modes in parallel"
        )
        
        # HTTP configuration
        parser.add_argument(
            "--host", 
            default="0.0.0.0",
            help="Host for HTTP server (default: 0.0.0.0)"
        )
        parser.add_argument(
            "--port", 
            type=int,
            default=8000,
            help="Port for HTTP server (default: 8000)"
        )
        
        # Red Bee configuration (required)
        parser.add_argument(
            "--customer", 
            default=os.getenv("REDBEE_CUSTOMER"),
            help="Red Bee customer identifier (required)"
        )
        parser.add_argument(
            "--business-unit", 
            default=os.getenv("REDBEE_BUSINESS_UNIT"),
            help="Red Bee business unit identifier (required)"
        )
        
        # Red Bee configuration (optional)
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
            default=os.getenv("REDBEE_CONFIG_ID", "sandwich"),
            help="Configuration ID (optional)"
        )
        
        return parser.parse_args()

    def create_config(self, args: argparse.Namespace):
        """Creates RedBeeConfig from parsed arguments."""
        from .models import RedBeeConfig
        
        return RedBeeConfig(
            customer=args.customer or "",
            business_unit=args.business_unit or "",
            exposure_base_url=args.exposure_base_url,
            username=args.username,
            session_token=args.session_token,
            device_id=args.device_id,
            config_id=args.config_id
        )

    def setup_environment(self, config):
        """Configure environment variables for subprocesses."""
        os.environ["REDBEE_CUSTOMER"] = config.customer
        os.environ["REDBEE_BUSINESS_UNIT"] = config.business_unit
        os.environ["REDBEE_EXPOSURE_BASE_URL"] = config.exposure_base_url
        if config.username:
            os.environ["REDBEE_USERNAME"] = config.username
        if config.session_token:
            os.environ["REDBEE_SESSION_TOKEN"] = config.session_token
        if config.device_id:
            os.environ["REDBEE_DEVICE_ID"] = config.device_id
        if config.config_id:
            os.environ["REDBEE_CONFIG_ID"] = config.config_id

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down...")
        sys.exit(0)

    async def run_stdio_server(self) -> None:
        """Run the MCP server in stdio mode."""
        from .server import main as server_main
        
        logger.info("Starting MCP server in stdio mode")
        
        # Configure signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            await server_main()
        except Exception as e:
            logger.error(f"Error running stdio server: {e}")
            raise

    async def run_http_server(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Run the HTTP/SSE server."""
        from .http_server import start_http_server
        
        logger.info(f"Starting MCP HTTP server on {host}:{port}")
        
        try:
            await start_http_server(self.config, host, port)
        except Exception as e:
            logger.error(f"Error running HTTP server: {e}")
            raise

    def run_stdio_process(self):
        """Run the stdio server in a separate process."""
        try:
            asyncio.run(self.run_stdio_server())
        except KeyboardInterrupt:
            logger.info("Stdio server interrupted")
        except Exception as e:
            logger.error(f"Error in stdio process: {e}")

    def run_http_process(self, host: str, port: int):
        """Run the HTTP server in a separate process."""
        try:
            asyncio.run(self.run_http_server(host, port))
        except KeyboardInterrupt:
            logger.info("HTTP server interrupted")
        except Exception as e:
            logger.error(f"Error in HTTP process: {e}")

    async def run_both_modes(self, host: str, port: int) -> None:
        """Run both servers in parallel in separate processes."""
        logger.info("Starting both modes in parallel")
        
        # Start stdio process
        stdio_process = mp.Process(target=self.run_stdio_process)
        stdio_process.start()
        
        # Start HTTP process  
        http_process = mp.Process(target=self.run_http_process, args=(host, port))
        http_process.start()
        
        try:
            # Wait for both processes to finish
            stdio_process.join()
            http_process.join()
        except KeyboardInterrupt:
            logger.info("Stopping both servers...")
            stdio_process.terminate()
            http_process.terminate()
            stdio_process.join()
            http_process.join()

    async def run(self) -> None:
        """Main entry point."""
        try:
            args = self.parse_args()
            self.config = self.create_config(args)
            
            # Configure environment
            self.setup_environment(self.config)
            
            # Launch server(s) according to chosen mode
            if args.stdio:
                await self.run_stdio_server()
            elif args.http:
                await self.run_http_server(args.host, args.port)
            elif args.both:
                await self.run_both_modes(args.host, args.port)
                
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            raise

def main():
    """Main entry point for CLI."""
    try:
        cli = RedBeeMCPCLI()
        
        # Check if arguments were provided
        args = sys.argv[1:]
        if not args:
            # Show help if no options are specified
            parser = argparse.ArgumentParser(
                description="Red Bee MCP Server - MCP interface for Red Bee Media APIs"
            )
            parser.add_argument("--stdio", help="Stdio mode for local AI agents")
            parser.add_argument("--http", help="HTTP/SSE mode for website")
            parser.add_argument("--both", help="Both modes in parallel")
            parser.print_help()
            return
            
        asyncio.run(cli.run())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"CLI error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 