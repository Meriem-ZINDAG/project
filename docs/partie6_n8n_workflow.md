# Partie 6 : Agent IA & Automatisation avec n8n

## 🤖 Architecture du Workflow

### Vue d'Ensemble

Le workflow n8n automatise l'ensemble du processus d'optimisation VRP, de la récupération des données jusqu'à la notification des résultats. Il permet une exécution planifiée ou déclenchée par événement.

```
┌─────────────────────────────────────────────────────────────────┐
│                      WORKFLOW N8N - VRP                         │
└─────────────────────────────────────────────────────────────────┘

    1. DÉCLENCHEUR
         │
         ├─ Schedule (Cron) : Exécution quotidienne à 6h
         ├─ Webhook : Déclenchement à la demande
         └─ Manual Trigger : Test/Debug
         │
         ▼
    2. PRÉPARATION DES DONNÉES
         │
         ├─ Récupération des données clients (Base de données/API)
         ├─ Validation et nettoyage
         └─ Formatage JSON
         │
         ▼
    3. APPEL API VRP
         │
         ├─ POST /optimize
         ├─ Configuration des paramètres
         └─ Envoi des données clients
         │
         ▼
    4. TRAITEMENT DES RÉSULTATS
         │
         ├─ GET /results/{result_id}
         ├─ Extraction des métriques
         └─ Préparation du rapport
         │
         ▼
    5. RÉCUPÉRATION DES VISUALISATIONS
         │
         ├─ GET /visualizations/{result_id}/routes
         ├─ GET /visualizations/{result_id}/comparison
         └─ GET /visualizations/{result_id}/timeline
         │
         ▼
    6. GÉNÉRATION DU RAPPORT
         │
         ├─ Compilation des données
         ├─ Formatage HTML/PDF
         └─ Ajout des visualisations
         │
         ▼
    7. NOTIFICATION ET DISTRIBUTION
         │
         ├─ Email : Envoi du rapport aux responsables
         ├─ Slack/Teams : Notification équipe
         ├─ Stockage : Sauvegarde dans cloud (S3, Drive)
         └─ Webhook : Notification autres systèmes
```

## 🔧 Configuration du Workflow n8n

### Prérequis

1. **Installation de n8n**
   ```bash
   npm install -g n8n
   # ou
   docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n
   ```

2. **API Flask VRP en fonctionnement**
   ```bash
   python main.py api
   # L'API doit être accessible sur http://localhost:5000
   ```

3. **Comptes configurés**
   - Compte email (SMTP)
   - Slack workspace (optionnel)
   - Stockage cloud (optionnel)

### Structure du Workflow

Le fichier `n8n/workflow_vrp.json` contient la configuration complète du workflow.

## 📋 Nœuds du Workflow

### 1. Nœud Déclencheur (Trigger)

#### A. Schedule Trigger
```json
{
  "name": "Schedule Trigger",
  "type": "n8n-nodes-base.scheduleTrigger",
  "typeVersion": 1,
  "position": [250, 300],
  "parameters": {
    "rule": {
      "interval": [
        {
          "field": "cronExpression",
          "expression": "0 6 * * *"
        }
      ]
    }
  }
}
```
- **Fonction** : Déclenche automatiquement à 6h du matin chaque jour
- **Configuration** : Expression cron modifiable

#### B. Webhook Trigger (optionnel)
```json
{
  "name": "Webhook",
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 1,
  "position": [250, 450],
  "parameters": {
    "path": "vrp-optimize",
    "method": "POST",
    "responseMode": "responseNode"
  }
}
```
- **Fonction** : Permet le déclenchement via HTTP POST
- **URL** : `http://localhost:5678/webhook/vrp-optimize`

### 2. Préparation des Données

#### Function Node - Préparer Configuration
```json
{
  "name": "Préparer Configuration",
  "type": "n8n-nodes-base.function",
  "typeVersion": 1,
  "position": [450, 300],
  "parameters": {
    "functionCode": "// Configuration par défaut\nconst config = {\n  num_vehicles: 3,\n  vehicle_capacity: 50,\n  weight_distance: 1.0,\n  weight_priority: 0.5,\n  weight_time: 0.3,\n  time_limit: 30\n};\n\n// Préparer le payload\nconst payload = {\n  config: config\n};\n\nreturn {\n  json: payload\n};"
  }
}
```

### 3. Appel API VRP

#### HTTP Request Node - Optimiser
```json
{
  "name": "Appel API Optimisation",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 1,
  "position": [650, 300],
  "parameters": {
    "method": "POST",
    "url": "http://localhost:5000/optimize",
    "options": {
      "timeout": 60000
    },
    "bodyParametersJson": "={{ JSON.stringify($json) }}",
    "headerParametersJson": "{\n  \"Content-Type\": \"application/json\"\n}"
  }
}
```

### 4. Extraction des Résultats

#### Function Node - Extraire Métriques
```json
{
  "name": "Extraire Métriques",
  "type": "n8n-nodes-base.function",
  "typeVersion": 1,
  "position": [850, 300],
  "parameters": {
    "functionCode": "const response = $input.first().json;\n\n// Extraire les informations clés\nconst metrics = {\n  result_id: response.result_id,\n  total_distance: response.summary.total_distance,\n  num_vehicles_used: response.summary.num_vehicles_used,\n  clients_served: response.summary.clients_served,\n  service_rate: response.summary.service_rate,\n  recommendations: response.recommendations,\n  improvement: response.comparison.improvement_percentage,\n  timestamp: new Date().toISOString()\n};\n\nreturn {\n  json: metrics\n};"
  }
}
```

### 5. Récupération des Visualisations

#### HTTP Request Nodes - Télécharger Images

**Routes**
```json
{
  "name": "Télécharger Routes",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 1,
  "position": [1050, 200],
  "parameters": {
    "method": "GET",
    "url": "=http://localhost:5000/visualizations/{{$json.result_id}}/routes",
    "options": {
      "response": {
        "response": {
          "responseFormat": "file"
        }
      }
    }
  }
}
```

**Comparaison**
```json
{
  "name": "Télécharger Comparaison",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 1,
  "position": [1050, 300],
  "parameters": {
    "method": "GET",
    "url": "=http://localhost:5000/visualizations/{{$json.result_id}}/comparison"
  }
}
```

**Timeline**
```json
{
  "name": "Télécharger Timeline",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 1,
  "position": [1050, 400],
  "parameters": {
    "method": "GET",
    "url": "=http://localhost:5000/visualizations/{{$json.result_id}}/timeline"
  }
}
```

### 6. Génération du Rapport

#### Function Node - Créer Rapport HTML
```json
{
  "name": "Créer Rapport HTML",
  "type": "n8n-nodes-base.function",
  "typeVersion": 1,
  "position": [1250, 300],
  "parameters": {
    "functionCode": "const metrics = $input.first().json;\n\nconst html = `\n<!DOCTYPE html>\n<html>\n<head>\n  <meta charset=\"UTF-8\">\n  <title>Rapport VRP - ${metrics.result_id}</title>\n  <style>\n    body { font-family: Arial, sans-serif; margin: 40px; }\n    h1 { color: #2c3e50; }\n    .metric { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }\n    .metric-value { font-size: 24px; color: #3498db; font-weight: bold; }\n    .recommendation { background: #fff3cd; padding: 10px; margin: 5px 0; border-left: 4px solid #ffc107; }\n  </style>\n</head>\n<body>\n  <h1>🚛 Rapport d'Optimisation VRP</h1>\n  <p><strong>Date :</strong> ${metrics.timestamp}</p>\n  <p><strong>ID Résultat :</strong> ${metrics.result_id}</p>\n  \n  <h2>📊 Métriques Principales</h2>\n  <div class=\"metric\">\n    <strong>Distance Totale :</strong>\n    <div class=\"metric-value\">${metrics.total_distance.toFixed(2)} unités</div>\n  </div>\n  \n  <div class=\"metric\">\n    <strong>Véhicules Utilisés :</strong>\n    <div class=\"metric-value\">${metrics.num_vehicles_used}</div>\n  </div>\n  \n  <div class=\"metric\">\n    <strong>Clients Servis :</strong>\n    <div class=\"metric-value\">${metrics.clients_served} (${metrics.service_rate.toFixed(1)}%)</div>\n  </div>\n  \n  <div class=\"metric\">\n    <strong>Amélioration vs Non-Optimisé :</strong>\n    <div class=\"metric-value\">${metrics.improvement.toFixed(1)}%</div>\n  </div>\n  \n  <h2>💡 Recommandations</h2>\n  ${metrics.recommendations.map(r => `<div class=\"recommendation\">${r}</div>`).join('')}\n  \n  <h2>📈 Visualisations</h2>\n  <p>Les visualisations sont disponibles en pièces jointes.</p>\n</body>\n</html>\n`;\n\nreturn {\n  json: {\n    html: html,\n    metrics: metrics\n  }\n};"
  }
}
```

### 7. Notification Email

#### Send Email Node
```json
{
  "name": "Envoyer Email",
  "type": "n8n-nodes-base.emailSend",
  "typeVersion": 1,
  "position": [1450, 300],
  "parameters": {
    "fromEmail": "vrp@company.com",
    "toEmail": "logistics@company.com",
    "subject": "=Rapport VRP - {{$json.metrics.result_id}}",
    "text": "=Rapport d'optimisation VRP disponible",
    "html": "={{$json.html}}",
    "attachments": "=image1,image2,image3",
    "options": {}
  },
  "credentials": {
    "smtp": {
      "id": "1",
      "name": "SMTP account"
    }
  }
}
```

### 8. Notification Slack (Optionnel)

#### Slack Node
```json
{
  "name": "Notifier Slack",
  "type": "n8n-nodes-base.slack",
  "typeVersion": 1,
  "position": [1450, 450],
  "parameters": {
    "channel": "#logistics",
    "text": "=🚛 Nouvelle optimisation VRP terminée!\n\n*Distance totale:* {{$json.metrics.total_distance.toFixed(2)}} unités\n*Véhicules utilisés:* {{$json.metrics.num_vehicles_used}}\n*Taux de service:* {{$json.metrics.service_rate.toFixed(1)}}%\n*Amélioration:* {{$json.metrics.improvement.toFixed(1)}}%\n\nConsultez le rapport par email pour plus de détails.",
    "attachments": [],
    "otherOptions": {}
  },
  "credentials": {
    "slackApi": {
      "id": "2",
      "name": "Slack account"
    }
  }
}
```

## 🚀 Déploiement et Utilisation

### Installation Locale

1. **Cloner le projet**
   ```bash
   git clone <repository>
   cd project
   ```

2. **Installer les dépendances Python**
   ```bash
   pip install -r requirements.txt
   ```

3. **Démarrer l'API Flask**
   ```bash
   python main.py api
   # L'API sera accessible sur http://localhost:5000
   ```

4. **Installer n8n**
   ```bash
   npm install -g n8n
   ```

5. **Démarrer n8n**
   ```bash
   n8n start
   # Interface accessible sur http://localhost:5678
   ```

6. **Importer le workflow**
   - Ouvrir http://localhost:5678
   - Créer un nouveau workflow
   - Importer le fichier `n8n/workflow_vrp.json`

### Configuration des Credentials

#### SMTP (Email)
- Type : SMTP
- Host : smtp.gmail.com (ou votre serveur SMTP)
- Port : 587
- User : votre-email@gmail.com
- Password : votre-mot-de-passe

#### Slack (Optionnel)
- Type : Slack API
- Access Token : Obtenir sur https://api.slack.com/apps

### Test du Workflow

1. **Test Manuel**
   - Cliquer sur "Execute Workflow" dans n8n
   - Vérifier que tous les nœuds s'exécutent correctement
   - Vérifier la réception de l'email

2. **Test via Webhook**
   ```bash
   curl -X POST http://localhost:5678/webhook/vrp-optimize \
     -H "Content-Type: application/json" \
     -d '{
       "config": {
         "num_vehicles": 3,
         "vehicle_capacity": 50
       }
     }'
   ```

3. **Test Planifié**
   - Activer le workflow
   - Attendre l'exécution planifiée
   - Vérifier les logs

## 📊 Monitoring et Logs

### Logs n8n

Les logs sont accessibles dans l'interface n8n :
- Menu "Executions" : Historique complet
- Détails par nœud : Voir les données entrées/sorties
- Erreurs : Affichage des stack traces

### Logs API Flask

```bash
# Dans le terminal où l'API est lancée
# Les logs affichent :
# - Requêtes reçues
# - Temps de traitement
# - Erreurs éventuelles
```

## 🔒 Sécurité

### Bonnes Pratiques

1. **Variables d'Environnement**
   - Ne jamais commit les credentials
   - Utiliser des variables d'environnement n8n
   - Fichier `.env` pour les secrets

2. **API**
   - Ajouter une authentification (API Key)
   - Limiter les taux de requêtes
   - HTTPS en production

3. **n8n**
   - Authentification activée
   - Webhook sécurisé avec token
   - Backup régulier des workflows

## 🌐 Déploiement en Production

### Option 1 : Docker Compose

```yaml
version: '3.8'

services:
  vrp-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./output:/app/output

  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=changeme
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

### Option 2 : Services Cloud

1. **API Flask** : 
   - AWS Elastic Beanstalk
   - Google Cloud Run
   - Heroku

2. **n8n** :
   - n8n.cloud (SaaS)
   - AWS ECS
   - DigitalOcean App Platform

## 📈 Améliorations Possibles

### Extensions du Workflow

1. **Base de Données**
   - Stockage des résultats historiques
   - Analyse des tendances
   - Comparaisons période sur période

2. **Machine Learning**
   - Prédiction de la demande
   - Ajustement automatique des paramètres
   - Détection d'anomalies

3. **Intégrations**
   - ERP (SAP, Oracle)
   - TMS (Transportation Management System)
   - GPS Tracking temps réel

4. **Dashboards**
   - Grafana pour visualisation temps réel
   - Power BI / Tableau pour analytics
   - Alertes personnalisées

## 📚 Ressources

### Documentation

- **n8n** : https://docs.n8n.io/
- **Flask** : https://flask.palletsprojects.com/
- **OR-Tools** : https://developers.google.com/optimization

### Communauté

- **Forum n8n** : https://community.n8n.io/
- **GitHub** : https://github.com/n8n-io/n8n

### Support

Pour toute question ou problème :
1. Consulter la documentation
2. Vérifier les logs
3. Contacter l'équipe de support
