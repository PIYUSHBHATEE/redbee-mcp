#!/bin/bash

# Script de démarrage pour AWS EC2
# Ce script configure et lance le serveur Red Bee MCP en mode production

set -e  # Arrêter en cas d'erreur

# Configuration des variables
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$PROJECT_DIR/redbee-mcp.pid"

# Créer le dossier de logs
mkdir -p "$LOG_DIR"

cd "$PROJECT_DIR"

echo "=== Démarrage du serveur Red Bee MCP pour AWS EC2 ==="
echo "Date: $(date)"
echo "Répertoire projet: $PROJECT_DIR"

# Vérifier si Python 3 est disponible
if ! command -v python3 &> /dev/null; then
    echo "Erreur: Python 3 n'est pas installé"
    exit 1
fi

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "$VENV_DIR" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv "$VENV_DIR"
fi

# Activer l'environnement virtuel
echo "Activation de l'environnement virtuel..."
source "$VENV_DIR/bin/activate"

# Mettre à jour pip
echo "Mise à jour de pip..."
pip install --upgrade pip

# Installer les dépendances
echo "Installation des dépendances..."
pip install -r requirements.txt

# Configuration des variables d'environnement pour la production
export PYTHONPATH="$PROJECT_DIR/src"
export REDBEE_CUSTOMER="${REDBEE_CUSTOMER:-TV5MONDE}"
export REDBEE_BUSINESS_UNIT="${REDBEE_BUSINESS_UNIT:-TV5MONDEplus}"
export REDBEE_EXPOSURE_BASE_URL="${REDBEE_EXPOSURE_BASE_URL:-https://exposure.api.redbee.live}"
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"

# Afficher la configuration
echo "Configuration du serveur:"
echo "  Customer: $REDBEE_CUSTOMER"
echo "  Business Unit: $REDBEE_BUSINESS_UNIT"
echo "  Base URL: $REDBEE_EXPOSURE_BASE_URL"
echo "  Host: $HOST"
echo "  Port: $PORT"

# Vérifier si le port est libre
if netstat -tuln | grep -q ":$PORT "; then
    echo "Attention: Le port $PORT est déjà utilisé"
    echo "Processus utilisant le port:"
    netstat -tulnp | grep ":$PORT "
fi

# Arrêter le processus existant s'il existe
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "Arrêt du processus existant (PID: $OLD_PID)..."
        kill "$OLD_PID"
        sleep 2
    fi
    rm -f "$PID_FILE"
fi

# Lancer le serveur en arrière-plan avec logging
echo "Lancement du serveur Red Bee MCP..."
echo "URL d'accès: http://$HOST:$PORT"
echo "Logs disponibles dans: $LOG_DIR/"

nohup python -m redbee_mcp.server \
    > "$LOG_DIR/server.log" \
    2> "$LOG_DIR/error.log" &

# Sauvegarder le PID
echo $! > "$PID_FILE"

# Attendre que le serveur démarre
sleep 3

# Vérifier que le serveur fonctionne
if ps -p "$(cat "$PID_FILE")" > /dev/null 2>&1; then
    echo "✅ Serveur démarré avec succès!"
    echo "PID: $(cat "$PID_FILE")"
    echo "Pour arrêter le serveur: kill $(cat "$PID_FILE")"
    echo "Pour voir les logs: tail -f $LOG_DIR/server.log"
    
    # Test de connectivité
    sleep 2
    if curl -s "http://localhost:$PORT/health" > /dev/null; then
        echo "✅ Test de santé réussi"
    else
        echo "⚠️  Test de santé échoué - vérifiez les logs"
    fi
else
    echo "❌ Erreur: Le serveur ne s'est pas lancé correctement"
    echo "Vérifiez les logs d'erreur: cat $LOG_DIR/error.log"
    exit 1
fi 