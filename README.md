# Red Bee Media MCP Server

## Vue d'ensemble

Ce serveur MCP (Model Context Protocol) fournit une interface complète pour interagir avec la plateforme OTT (Over-The-Top) de **Red Bee Media** via son API Exposure. Il permet d'intégrer facilement les fonctionnalités de streaming vidéo, gestion d'utilisateurs, analytics et bien plus dans des applications basées sur MCP comme Cursor.

### Qu'est-ce que Red Bee Media ?

Red Bee Media est une plateforme OTT professionnelle qui fournit des solutions complètes pour :
- **Streaming vidéo** : Diffusion de contenu en direct et à la demande
- **Gestion d'utilisateurs** : Authentification et droits d'accès
- **Analytics** : Métriques de visionnage et engagement
- **Monétisation** : Abonnements et achats de contenu

## Fonctionnalités

### 🎬 Gestion de Contenu
- **Recherche de contenu** avec filtres (genre, date, popularité)
- **Détails des assets** (métadonnées, durée, langues)
- **Informations de lecture** (URLs de streaming, DRM, sous-titres)
- **Catégories disponibles** sur la plateforme

### 👤 Gestion d'Utilisateurs
- **Authentification** (avec credentials ou anonyme)
- **Profils utilisateurs** (informations limitées via Exposure API)
- **Droits d'accès** (entitlements) par utilisateur
- **Mise à jour de profils** (nécessite API Management)

### 📊 Analytics et Métriques
- **Analytics de contenu** (vues, temps de visionnage, taux de completion)
- **Historique de visionnage** par utilisateur
- **Métriques globales** de la plateforme

### 🛒 Commerce (Information uniquement)
- **Informations sur les commandes** (nécessite API Management)
- **Gestion d'abonnements** (nécessite API Management)
- **Statut des produits** (nécessite API Management)

### ⚙️ Configuration
- **Configuration de l'unité commerciale**
- **Informations sur les produits disponibles**
- **Paramètres de la plateforme**

## Installation

### 1. Cloner le repository
```bash
git clone <repository-url>
cd redbee-MCP
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Installer en mode développement
```bash
pip install -e .
```

## Configuration

### Variables d'environnement

Créez un fichier `.env` basé sur `env.example` :

```env
# Configuration Red Bee Media (OBLIGATOIRE)
REDBEE_CUSTOMER=your_customer_id
REDBEE_BUSINESS_UNIT=your_business_unit

# URL de l'API Exposure (par défaut)
REDBEE_EXPOSURE_BASE_URL=https://exposure.api.redbee.live

# Authentification (optionnel)
REDBEE_USERNAME=your_username
REDBEE_PASSWORD=your_password
REDBEE_SESSION_TOKEN=your_session_token
REDBEE_DEVICE_ID=your_device_id

# Paramètres de connexion
REDBEE_TIMEOUT=30
```

### Configuration minimale requise

Les seules variables **obligatoires** sont :
- `REDBEE_CUSTOMER` : ID du client Red Bee Media
- `REDBEE_BUSINESS_UNIT` : ID de l'unité commerciale

## Configuration pour Cursor

### Ajouter à la configuration MCP de Cursor

Éditez votre fichier de configuration MCP dans Cursor :

**macOS/Linux :** `~/.cursor/mcp_settings.json`
**Windows :** `%APPDATA%\Cursor\User\mcp_settings.json`

```json
{
  "mcpServers": {
    "redbee-mcp": {
      "command": "python",
      "args": ["-m", "redbee_mcp.server"],
      "cwd": "/chemin/vers/redbee-MCP",
      "env": {
        "PYTHONPATH": "/chemin/vers/redbee-MCP/src",
        "REDBEE_CUSTOMER": "votre_customer_id",
        "REDBEE_BUSINESS_UNIT": "votre_business_unit",
        "REDBEE_EXPOSURE_BASE_URL": "https://exposure.api.redbee.live"
      }
    }
  }
}
```

### Redémarrer Cursor

Redémarrez Cursor pour charger la nouvelle configuration MCP.

## Utilisation

### Exemples d'utilisation dans Cursor

#### 1. Rechercher du contenu
```
Recherche des films d'action sur Red Bee Media
```

#### 2. Obtenir les détails d'un contenu
```
Récupère les détails du contenu avec l'ID "asset_12345"
```

#### 3. Authentifier un utilisateur
```
Authentifie l'utilisateur "john.doe@example.com" avec le mot de passe "motdepasse"
```

#### 4. Vérifier les droits d'accès d'un utilisateur
```
Vérifie les droits d'accès de l'utilisateur "user_789"
```

#### 5. Obtenir les analytics d'un contenu
```
Récupère les statistiques de visionnage du contenu "asset_12345" pour le mois dernier
```

## Outils MCP Disponibles

### 🎬 Contenu (4 outils)
- `search_content` : Recherche de contenu
- `get_content_details` : Détails d'un contenu
- `get_content_playback_info` : Informations de lecture
- `list_content_categories` : Catégories disponibles

### 👤 Utilisateurs (4 outils)
- `authenticate_user` : Authentification
- `get_user_profile` : Profil utilisateur
- `update_user_profile` : Mise à jour de profil
- `get_user_entitlements` : Droits d'accès

### 🛒 Commandes (4 outils)
- `create_purchase_order` : Création de commande
- `get_order_status` : Statut de commande
- `list_user_orders` : Commandes d'un utilisateur
- `process_subscription` : Gestion d'abonnements

### ⚙️ Configuration (3 outils)
- `get_business_unit_config` : Configuration de l'unité
- `list_available_products` : Produits disponibles
- `get_product_details` : Détails d'un produit

### 📊 Analytics (3 outils)
- `get_content_analytics` : Analytics de contenu
- `get_user_viewing_history` : Historique de visionnage
- `get_platform_metrics` : Métriques globales

**Total : 18 outils MCP**

## Limitations importantes

### API Exposure vs API Management

L'**API Exposure** de Red Bee Media est principalement conçue pour :
- ✅ Authentification des utilisateurs finaux
- ✅ Recherche et accès au contenu
- ✅ Vérification des droits d'accès (entitlements)
- ✅ Informations de lecture (playback)
- ✅ Analytics de base

Pour les opérations avancées, l'**API Management** est nécessaire :
- ❌ Création/modification d'utilisateurs
- ❌ Gestion des abonnements et paiements
- ❌ Administration de la plateforme
- ❌ Configuration des produits et prix

### Authentification

Plusieurs modes d'authentification sont supportés :
1. **Anonyme** : Accès limité au contenu public
2. **Credentials** : Authentification avec username/password
3. **Token de session** : Utilisation d'un token existant

## Tests et développement

### Tester le serveur MCP
```bash
# Test simple
python -m redbee_mcp.server

# Avec variables d'environnement
REDBEE_CUSTOMER=test REDBEE_BUSINESS_UNIT=demo python -m redbee_mcp.server
```

### Développement
```bash
# Installation en mode développement
pip install -e .

# Tests (si disponibles)
python -m pytest tests/
```

## Dépannage

### Problèmes courants

#### 1. "Erreur de configuration"
```
Erreur de configuration: REDBEE_CUSTOMER et REDBEE_BUSINESS_UNIT sont requis
```
**Solution :** Vérifiez que les variables d'environnement sont correctement définies.

#### 2. "HTTP 404" lors des requêtes
```
Erreur API Red Bee: HTTP 404
```
**Solution :** Vérifiez que vos identifiants Customer et Business Unit sont corrects pour votre compte Red Bee Media.

#### 3. "Aucun outil chargé dans Cursor"
**Solution :** 
- Vérifiez le chemin dans la configuration MCP
- Redémarrez Cursor
- Vérifiez les logs de Cursor pour les erreurs

### Logs et debug

Les logs sont disponibles via la sortie standard :
```bash
# Activer les logs détaillés
export PYTHONPATH=/chemin/vers/redbee-MCP/src
python -m redbee_mcp.server
```

## Support et documentation

### Documentation Red Bee Media
- **Site officiel :** https://redbee.live
- **Documentation API :** https://redbee.live/docs/API/
- **Player JavaScript :** https://redbee.live/docs/JavaScript-Player/

### Architecture Red Bee Media
- **Exposure API :** Authentification et contenu (utilisé par ce MCP)
- **Management API :** Administration et gestion
- **Analytics API :** Métriques avancées
- **Eventsink API :** Événements analytiques

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Contribution

Les contributions sont les bienvenues ! Veuillez :
1. Fork le repository
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

---

**Note :** Ce serveur MCP est basé sur l'API Exposure de Red Bee Media et respecte les limitations de cette API. Pour les fonctionnalités avancées, une intégration avec l'API Management de Red Bee Media est nécessaire. 