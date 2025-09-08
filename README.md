# Système à deux drones – Détection et Brumisation (simulation)

Ce projet simule :
- Drone 1 (Détection) : caméra + IA + GPS → envoie zones stressées au serveur central.
- Serveur central : stockage JSON des points stressés et génération file de brumisation.
- Drone 2 (Brumisation) : lit la file et applique une brumisation proportionnelle au niveau de stress.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Exécution
```bash
python main.py --mission sample_mission.json --seed 42 --storage server_data.json
```

- `--mission` : fichier JSON définissant les zones.
- `--seed` : graine pseudo-aléatoire (optionnel) pour reproductibilité.
- `--storage` : fichier de persistance côté serveur (JSON).

## Schéma logique
- Drone 1 → capture image → API IA → verdict (stress, niveau) → Serveur central (stockage)
- Serveur central → file de brumisation ordonnée par niveau de stress
- Drone 2 → dépile les tâches et pulvérise avec intensité (low/medium/high)

## Structure
```
main.py
sample_mission.json

drone_agri/
  ai_api.py        # Stub client API IA (remplacer par votre vrai service)
  camera.py        # Caméra RGB (stub)
  drones.py        # Logique Drone 1 & Drone 2
  mission.py       # Chargement des zones/Mission
  models.py        # Modèles de données
  server.py        # Serveur central (JSON persistence + file brumisation)
```

## Notes
- Le client `ai_api.py` est un stub (simulation). Remplacez `analyze_image()` par votre appel API réel (HTTP/GRPC) et parsez la réponse.
- La logique de volume/intensité est simple et ajustable selon vos paramètres réels.
- Vous pouvez relancer seulement le Drone 2 pour continuer la brumisation en réutilisant `--storage`.
