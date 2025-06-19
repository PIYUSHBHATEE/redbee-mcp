#!/usr/bin/env python3
"""
Main entry point for Red Bee MCP server
"""

import asyncio

def main():
    """Entry point for uvx script - Lance directement le serveur MCP"""
    from .server import main as server_main
    asyncio.run(server_main())

if __name__ == "__main__":
    main() 