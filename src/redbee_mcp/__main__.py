#!/usr/bin/env python3
"""
Point d'entrée principal pour le module redbee_mcp
- Par défaut: lance le serveur HTTP (pour déploiement AWS)
- Pour Cursor: utilisez server_hybrid directement
"""

import sys
from .server import start_server

if __name__ == "__main__":
    # Le serveur HTTP est le comportement par défaut pour AWS
    start_server() 