#!/bin/bash

# Se positionner dans le dossier du script
cd "$(dirname "$0")"

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
  echo "Création de l'environnement virtuel..."
  python3 -m venv venv
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances
echo "Installation des dépendances..."
pip install -r requirements.txt

# Définir les variables d'environnement
export PYTHONPATH=$(pwd)/src
export REDBEE_CUSTOMER=TV5MONDE
export REDBEE_BUSINESS_UNIT=TV5MONDEplus
export REDBEE_EXPOSURE_BASE_URL=https://exposure.api.redbee.live
export HOST=0.0.0.0
export PORT=8000

# Lancer le serveur HTTP MCP
echo "Lancement du serveur Red Bee MCP sur http://$HOST:$PORT"
python -m redbee_mcp.server
