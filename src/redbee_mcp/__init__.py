"""
RedBee MCP - Model Context Protocol pour RedBee Media OTT

Ce package fournit un serveur MCP pour interagir avec l'API RedBee Media OTT.
"""

__version__ = "0.1.0"
__author__ = "RedBee MCP Team"
__email__ = "mcp@redbee.com"

# Import du serveur principal (HTTP pour AWS)
from .server import app, start_server

# Import du client
from .client import RedBeeClient

__all__ = ["app", "start_server", "RedBeeClient"] 