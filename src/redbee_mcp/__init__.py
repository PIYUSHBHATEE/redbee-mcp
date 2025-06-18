"""
RedBee MCP - Model Context Protocol pour RedBee Media OTT

Ce package fournit un serveur MCP pour interagir avec l'API RedBee Media OTT.
"""

__version__ = "1.0.0"
__author__ = "RedBee MCP Team"
__email__ = "mcp@redbee.com"

# Import seulement le client par défaut pour éviter les dépendances lourdes
from .client import RedBeeClient

__all__ = ["RedBeeClient"]

# Import conditionnel du serveur (pour ne pas casser si FastAPI n'est pas installé)
try:
    from .server import app, start_server
    __all__.extend(["app", "start_server"])
except ImportError:
    # FastAPI non disponible, on ignore silencieusement
    pass 