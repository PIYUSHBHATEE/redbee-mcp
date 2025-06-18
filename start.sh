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

# Lancer le serveur MCP
echo "Lancement du MCP..."
python -m redbee_mcp.server
