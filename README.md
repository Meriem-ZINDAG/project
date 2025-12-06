# 🚛 Projet VRP - Optimisation de Tournées de Livraison

## 📋 Description

Ce projet implémente une solution complète d'optimisation de tournées de livraison (Vehicle Routing Problem - VRP) utilisant l'intelligence artificielle via OR-Tools de Google. Le système permet d'optimiser les itinéraires d'une flotte de véhicules en tenant compte de multiples contraintes (capacité, fenêtres horaires, priorités).

### ✨ Fonctionnalités Principales

- ✅ **Optimisation multi-contraintes** : Capacité, fenêtres horaires, temps de service, priorités
- ✅ **Visualisations graphiques** : Cartes des tournées, graphiques comparatifs, chronologie
- ✅ **Analyse détaillée** : Métriques de performance, recommandations d'amélioration
- ✅ **API REST Flask** : Interface programmable pour intégration
- ✅ **Workflow n8n** : Automatisation complète du processus
- ✅ **Modes d'exécution** : Interactif, automatique, API

## 🏗️ Architecture

```
projet-vrp-ia/
├── src/                        # Code source Python
│   ├── data_handler.py        # Gestion des données clients
│   ├── user_interface.py      # Interface utilisateur
│   ├── optimizer.py           # Algorithme VRP (OR-Tools)
│   ├── visualizer.py          # Génération des visualisations
│   ├── analyzer.py            # Analyse des résultats
│   └── api_server.py          # API Flask
├── docs/                       # Documentation
│   ├── partie1_comprehension.md    # Contexte et problématique VRP
│   ├── partie2_modelisation.md     # Formulation mathématique
│   └── partie6_n8n_workflow.md     # Documentation workflow n8n
├── n8n/                        # Workflow d'automatisation
│   └── workflow_vrp.json      # Configuration n8n
├── output/                     # Résultats et visualisations
│   └── .gitkeep
├── main.py                     # Point d'entrée principal
├── requirements.txt            # Dépendances Python
├── .gitignore                  # Fichiers à ignorer
└── README.md                   # Ce fichier
```

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Node.js 14+ (pour n8n, optionnel)

### Installation des Dépendances Python

```bash
# Cloner le dépôt
git clone <repository-url>
cd project

# Installer les dépendances
pip install -r requirements.txt
```

### Vérification de l'Installation

```bash
# Tester l'importation des modules
python -c "import ortools; import flask; import matplotlib; print('✓ Installation réussie!')"
```

## 💻 Utilisation

### Mode 1 : Interface Interactive

Lance l'application avec un menu interactif permettant de configurer tous les paramètres :

```bash
python main.py
```

Vous pourrez alors :
1. Configurer le nombre de véhicules et leur capacité
2. Ajuster les poids d'optimisation (distance, priorité, temps)
3. Choisir les options de visualisation et d'export

### Mode 2 : Exécution Automatique

Utilise les paramètres par défaut pour une exécution rapide :

```bash
python main.py auto
```

**Paramètres par défaut :**
- Véhicules : 3
- Capacité : 50 unités
- Poids distance : 1.0
- Poids priorité : 0.5
- Poids temps : 0.3
- Temps limite : 30 secondes

### Mode 3 : API REST Flask

Démarre le serveur API pour permettre l'automatisation via requêtes HTTP :

```bash
python main.py api
```

L'API sera accessible sur `http://localhost:5000`

#### Endpoints API

**1. Optimiser une tournée**
```bash
curl -X POST http://localhost:5000/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "num_vehicles": 3,
      "vehicle_capacity": 50,
      "weight_distance": 1.0,
      "weight_priority": 0.5,
      "weight_time": 0.3,
      "time_limit": 30
    }
  }'
```

**2. Récupérer les résultats**
```bash
curl http://localhost:5000/results/<result_id>
```

**3. Télécharger une visualisation**
```bash
curl http://localhost:5000/visualizations/<result_id>/routes -o routes.png
```

**4. Lister tous les résultats**
```bash
curl http://localhost:5000/list-results
```

**5. Configuration par défaut**
```bash
curl http://localhost:5000/default-config
```

**6. Health check**
```bash
curl http://localhost:5000/health
```

## 🤖 Automatisation avec n8n

### Installation de n8n

```bash
# Installation globale
npm install -g n8n

# Ou via Docker
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n
```

### Démarrage de n8n

```bash
n8n start
```

Interface accessible sur `http://localhost:5678`

### Import du Workflow

1. Ouvrir l'interface n8n (`http://localhost:5678`)
2. Créer un nouveau workflow
3. Cliquer sur les trois points (⋮) → "Import from File"
4. Sélectionner `n8n/workflow_vrp.json`
5. Configurer les credentials (SMTP, Slack)
6. Activer le workflow

### Configuration du Workflow

Le workflow automatise :
1. ⏰ **Déclenchement** : Planifié (cron) ou webhook
2. 📊 **Optimisation** : Appel API VRP
3. 📈 **Visualisations** : Téléchargement des graphiques
4. 📧 **Notification** : Email avec rapport HTML
5. 💬 **Alertes** : Message Slack (optionnel)

Voir [docs/partie6_n8n_workflow.md](docs/partie6_n8n_workflow.md) pour plus de détails.

## 📊 Données d'Exemple

Le projet inclut un jeu de données par défaut :
- **1 dépôt** : Point de départ et d'arrivée
- **20 clients** : Répartis géographiquement
- **Demandes** : Entre 2 et 10 unités par client
- **Priorités** : 3 niveaux (haute, moyenne, basse)
- **Fenêtres horaires** : Matinale (8h-12h), après-midi (13h-17h), flexible (0h-24h)

## 📈 Résultats

### Sorties Générées

1. **Visualisations PNG** (dans `output/`)
   - `vrp_routes.png` : Carte des tournées optimisées
   - `vrp_comparison.png` : Comparaison distances/charges
   - `vrp_timeline.png` : Chronologie des livraisons

2. **Fichiers de données**
   - `vrp_analysis.json` : Métriques complètes
   - `clients_data.csv` : Données des clients

3. **Affichage console**
   - Détails des tournées par véhicule
   - Métriques de performance
   - Recommandations d'amélioration

### Exemple de Résultats

```
📊 RÉSULTATS DE L'OPTIMISATION
════════════════════════════════════════

🎯 Distance totale optimale : 156.42 unités
📦 Charge totale transportée : 117 unités
🚛 Nombre de véhicules utilisés : 3

Véhicule 1 : 52.34 unités (7 clients)
Véhicule 2 : 48.91 unités (6 clients)
Véhicule 3 : 55.17 unités (7 clients)

💡 Amélioration : 28.5% vs solution non optimisée
```

## 📚 Documentation

### Documents Disponibles

1. **[Partie 1 : Compréhension](docs/partie1_comprehension.md)**
   - Contexte logistique
   - Description du problème VRP
   - Contraintes et objectifs

2. **[Partie 2 : Modélisation](docs/partie2_modelisation.md)**
   - Formulation mathématique
   - Variables et contraintes
   - Implémentation OR-Tools

3. **[Partie 6 : Workflow n8n](docs/partie6_n8n_workflow.md)**
   - Architecture du workflow
   - Configuration des nœuds
   - Déploiement et monitoring

## 🔧 Configuration Avancée

### Personnalisation des Données

Modifier les données dans `src/data_handler.py` :

```python
def get_default_clients_data() -> Dict:
    return {
        'id': [...],
        'nom': [...],
        'x': [...],
        'y': [...],
        'demande': [...],
        'temps_service': [...],
        'fenetre_debut': [...],
        'fenetre_fin': [...],
        'priorite': [...]
    }
```

### Ajustement des Paramètres

Les paramètres peuvent être ajustés :
- **Nombre de véhicules** : 1-10
- **Capacité** : 10-200 unités
- **Poids distance** : 0.0-10.0
- **Poids priorité** : 0.0-10.0
- **Poids temps** : 0.0-10.0
- **Temps limite** : 5-300 secondes

### Variables d'Environnement

Créer un fichier `.env` :

```env
FLASK_ENV=production
FLASK_PORT=5000
N8N_URL=http://localhost:5678
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=vrp@company.com
EMAIL_TO=logistics@company.com
```

## 🧪 Tests

### Test de l'Optimisation

```bash
python -c "from main import main_non_interactive; main_non_interactive()"
```

### Test de l'API

```bash
# Terminal 1 : Démarrer l'API
python main.py api

# Terminal 2 : Tester l'endpoint
curl -X POST http://localhost:5000/optimize \
  -H "Content-Type: application/json" \
  -d '{"config": {"num_vehicles": 3}}'
```

### Test du Workflow n8n

1. Démarrer l'API Flask
2. Démarrer n8n
3. Importer le workflow
4. Cliquer sur "Execute Workflow"

## 🐛 Dépannage

### Problème : OR-Tools ne s'installe pas

```bash
# Essayer avec pip upgrade
pip install --upgrade pip
pip install ortools

# Ou installer une version spécifique
pip install ortools==9.8.3296
```

### Problème : L'API ne démarre pas

```bash
# Vérifier le port
lsof -i :5000

# Changer le port si nécessaire
export FLASK_PORT=5001
python main.py api
```

### Problème : Pas de solution trouvée

- Augmenter le temps limite (time_limit)
- Augmenter la capacité des véhicules
- Augmenter le nombre de véhicules
- Réduire le poids de priorité

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit les changements (`git commit -m 'Ajout fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 👥 Auteurs

- Développé pour l'optimisation des tournées de livraison
- Utilise OR-Tools de Google
- Workflow n8n pour l'automatisation

## 🔗 Ressources

### Documentation Externe

- **OR-Tools** : https://developers.google.com/optimization
- **Flask** : https://flask.palletsprojects.com/
- **n8n** : https://docs.n8n.io/
- **Matplotlib** : https://matplotlib.org/

### Références Académiques

- Dantzig, G. B., & Ramser, J. H. (1959). "The Truck Dispatching Problem"
- Clarke, G., & Wright, J. W. (1964). "Scheduling of Vehicles from a Central Depot"
- Laporte, G. (2009). "Fifty Years of Vehicle Routing"

## 📞 Support

Pour toute question ou problème :
- 📧 Email : support@vrp-project.com
- 💬 Issues : GitHub Issues
- 📖 Documentation : Dossier `docs/`

---

**Note** : Ce projet est un système d'optimisation complet incluant la modélisation, l'optimisation, la visualisation et l'automatisation du problème VRP.