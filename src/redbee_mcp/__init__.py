"""
Red Bee MCP Server

MCP Server for Red Bee Media OTT Platform API
"""

__version__ = "1.0.0"
__author__ = "Tamsi Besson"

# Import only the client by default to avoid heavy dependencies
from .client import RedBeeClient
from .models import RedBeeConfig

# Conditional server import (to avoid breaking if FastAPI is not installed)
try:
    from .server import create_mcp_server
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

__all__ = ["RedBeeClient", "RedBeeConfig"]

if MCP_AVAILABLE:
    __all__.append("create_mcp_server") 