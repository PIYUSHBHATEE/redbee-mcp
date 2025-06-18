# Guide de déploiement Red Bee MCP sur AWS EC2

Ce guide vous explique comment déployer le serveur Red Bee MCP sur une instance AWS EC2 et l'exposer sur le port 8000.

## Prérequis

- Instance AWS EC2 avec Amazon Linux 2 ou Ubuntu
- Python 3.8+ installé
- Accès SSH à l'instance
- Port 8000 ouvert dans le Security Group

## Configuration du Security Group

Assurez-vous que votre Security Group EC2 autorise le trafic entrant sur le port 8000 :

```bash
# Via AWS CLI (optionnel)
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxx \
    --protocol tcp \
    --port 8000 \
    --cidr 0.0.0.0/0
```

## Installation sur EC2

### 1. Connexion et préparation

```bash
# Se connecter à l'instance EC2
ssh -i votre-cle.pem ec2-user@votre-ip-publique

# Mettre à jour le système
sudo yum update -y  # Amazon Linux 2
# ou
sudo apt update && sudo apt upgrade -y  # Ubuntu

# Installer Python 3 et pip (si nécessaire)
sudo yum install python3 python3-pip git -y  # Amazon Linux 2
# ou
sudo apt install python3 python3-pip python3-venv git -y  # Ubuntu
```

### 2. Clonage et installation

```bash
# Cloner le projet
git clone https://github.com/votre-username/redbee-MCP.git
cd redbee-MCP

# Rendre les scripts exécutables
chmod +x start.sh start-aws.sh

# Lancer l'installation et le serveur
./start-aws.sh
```

### 3. Configuration des variables d'environnement (optionnel)

Vous pouvez personnaliser la configuration en créant un fichier `.env` :

```bash
# Créer le fichier de configuration
cat > .env << EOF
REDBEE_CUSTOMER=TV5MONDE
REDBEE_BUSINESS_UNIT=TV5MONDEplus
REDBEE_EXPOSURE_BASE_URL=https://exposure.api.redbee.live
HOST=0.0.0.0
PORT=8000
EOF

# Charger les variables
source .env
```

## Service systemd (recommandé pour la production)

Pour que le serveur redémarre automatiquement :

### 1. Installation du service

```bash
# Adapter le chemin dans le fichier service si nécessaire
sudo cp redbee-mcp.service /etc/systemd/system/

# Recharger systemd
sudo systemctl daemon-reload

# Activer le service au démarrage
sudo systemctl enable redbee-mcp

# Démarrer le service
sudo systemctl start redbee-mcp
```

### 2. Gestion du service

```bash
# Voir le statut
sudo systemctl status redbee-mcp

# Arrêter le service
sudo systemctl stop redbee-mcp

# Redémarrer le service
sudo systemctl restart redbee-mcp

# Voir les logs
sudo journalctl -u redbee-mcp -f
```

## Vérification du déploiement

### 1. Test local

```bash
# Tester l'endpoint de santé
curl http://localhost:8000/health

# Lister les outils disponibles
curl http://localhost:8000/tools
```

### 2. Test externe

```bash
# Depuis votre machine locale (remplacer par l'IP publique de votre EC2)
curl http://votre-ip-publique-ec2:8000/health
```

### 3. Interface de documentation

Le serveur expose automatiquement une documentation Swagger/OpenAPI :
- **URL**: `http://votre-ip-publique-ec2:8000/docs`
- **Redoc**: `http://votre-ip-publique-ec2:8000/redoc`

## Utilisation de l'API

### Endpoints disponibles

- `GET /` - Informations générales du serveur
- `GET /health` - Vérification de santé
- `GET /tools` - Liste des outils MCP disponibles
- `POST /call` - Exécuter un outil MCP

### Exemple d'appel d'outil

```bash
# Créer une session anonyme
curl -X POST "http://votre-ip-publique-ec2:8000/call" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "create_anonymous_session",
       "arguments": {}
     }'

# Rechercher du contenu
curl -X POST "http://votre-ip-publique-ec2:8000/call" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "search_content",
       "arguments": {
         "query": "documentaire",
         "pageSize": 10
       }
     }'
```

## Monitoring et logs

### Logs du serveur

```bash
# Logs en temps réel
tail -f logs/server.log

# Logs d'erreur
tail -f logs/error.log

# Logs systemd (si service installé)
sudo journalctl -u redbee-mcp -f
```

### Monitoring des performances

```bash
# Vérifier l'utilisation des ressources
htop

# Vérifier les connexions réseau
netstat -tulnp | grep :8000

# Tester la charge
ab -n 100 -c 10 http://localhost:8000/health
```

## Sécurité

### 1. Firewall

```bash
# Configuration basique du firewall (Ubuntu)
sudo ufw allow ssh
sudo ufw allow 8000
sudo ufw enable
```

### 2. HTTPS (recommandé pour la production)

Pour sécuriser les communications, configurez un reverse proxy nginx avec SSL :

```bash
# Installer nginx
sudo yum install nginx -y  # Amazon Linux 2
# ou
sudo apt install nginx -y  # Ubuntu

# Configuration nginx (exemple)
sudo tee /etc/nginx/sites-available/redbee-mcp << EOF
server {
    listen 80;
    server_name votre-domaine.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Activer le site
sudo ln -s /etc/nginx/sites-available/redbee-mcp /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

## Dépannage

### Erreurs courantes

1. **Port 8000 déjà utilisé**
   ```bash
   sudo netstat -tulnp | grep :8000
   sudo kill -9 PID_DU_PROCESSUS
   ```

2. **Problèmes de permissions**
   ```bash
   sudo chown -R ec2-user:ec2-user /home/ec2-user/redbee-MCP
   ```

3. **Variables d'environnement manquantes**
   ```bash
   echo $REDBEE_CUSTOMER
   # Si vide, vérifiez votre configuration
   ```

### Support

- Logs détaillés : `tail -f logs/server.log`
- Status du service : `sudo systemctl status redbee-mcp`
- Test de connectivité : `curl -v http://localhost:8000/health` 