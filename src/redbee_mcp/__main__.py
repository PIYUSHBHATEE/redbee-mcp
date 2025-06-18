#!/usr/bin/env python3
"""
Point d'entrée principal pour le module redbee_mcp
Permet d'exécuter le serveur avec: python -m redbee_mcp
"""

from .server import start_server

if __name__ == "__main__":
    start_server() 