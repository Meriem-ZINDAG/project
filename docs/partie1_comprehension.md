# Partie 1 : Compréhension du Problème VRP

## 🎯 Contexte Logistique

### Description du Problème

Le **Vehicle Routing Problem (VRP)** ou **Problème de Tournées de Véhicules** est un problème d'optimisation combinatoire qui consiste à déterminer les itinéraires optimaux pour une flotte de véhicules devant livrer ou collecter des marchandises auprès d'un ensemble de clients.

### Éléments du Système

1. **Dépôt Central** 
   - Point de départ et d'arrivée de tous les véhicules
   - Coordonnées : (25.0, 25.0)
   - Fenêtre horaire : 0-1440 minutes (24h)

2. **Clients**
   - 20 clients répartis géographiquement
   - Chaque client a des caractéristiques spécifiques :
     * Position géographique (x, y)
     * Demande en unités de marchandise
     * Temps de service requis
     * Fenêtre horaire de livraison
     * Niveau de priorité

3. **Flotte de Véhicules**
   - Nombre de véhicules : configurable (par défaut 3)
   - Capacité identique pour tous les véhicules
   - Départ et retour au dépôt obligatoires

## 📋 Objectifs

### Objectif Principal
Minimiser la **distance totale parcourue** par l'ensemble de la flotte tout en respectant toutes les contraintes.

### Objectifs Secondaires
1. Équilibrer la charge de travail entre les véhicules
2. Respecter les priorités des clients
3. Optimiser le taux d'utilisation de la capacité des véhicules
4. Minimiser le nombre de véhicules utilisés

## 🔍 Contraintes du Problème

### 1. Contraintes de Capacité

- **Description** : Chaque véhicule a une capacité maximale qu'il ne peut pas dépasser
- **Formulation** : ∑(demandes des clients sur une tournée) ≤ Capacité du véhicule
- **Impact** : Limite le nombre de clients pouvant être servis par un seul véhicule
- **Données** :
  - Capacité par défaut : 50 unités
  - Demandes clients : entre 2 et 10 unités
  - Demande totale : 117 unités (pour 20 clients)

### 2. Contraintes de Fenêtres Horaires

- **Description** : Chaque client doit être servi dans sa fenêtre horaire spécifique
- **Types de fenêtres** :
  - Fenêtre complète : 0-1440 min (clients flexibles)
  - Fenêtre matinale : 480-720 min (8h-12h)
  - Fenêtre après-midi : 780-1020 min (13h-17h)
- **Impact** : Influence l'ordre de visite et peut nécessiter des temps d'attente

### 3. Contraintes de Temps de Service

- **Description** : Temps nécessaire pour décharger/charger chez chaque client
- **Plage** : 5 à 14 minutes selon le client
- **Impact** : Augmente le temps total de la tournée et affecte les fenêtres horaires

### 4. Contraintes de Priorité

- **Description** : Certains clients sont prioritaires et doivent être favorisés
- **Niveaux** :
  - Priorité 1 (Haute) : 13 clients - Clients VIP, livraisons urgentes
  - Priorité 2 (Moyenne) : 5 clients - Clients réguliers
  - Priorité 3 (Basse) : 2 clients - Livraisons flexibles
- **Impact** : Les clients haute priorité doivent être servis en priorité

### 5. Contraintes Opérationnelles

- Chaque client est visité au maximum une fois
- Tous les véhicules partent du dépôt et y retournent
- Un véhicule ne peut servir qu'un client à la fois
- Les distances sont euclidiennes (ligne droite)

## 🧮 Données du Problème

### Structure des Données Clients

```
Nombre total de lieux : 21 (1 dépôt + 20 clients)
Demande totale : 117 unités
Temps de service total : 188 minutes
```

### Répartition des Priorités

| Priorité | Nombre | Pourcentage |
|----------|---------|-------------|
| Haute (1) | 13 | 65% |
| Moyenne (2) | 5 | 25% |
| Basse (3) | 2 | 10% |

### Répartition des Fenêtres Horaires

| Type | Nombre | Plage horaire |
|------|--------|---------------|
| Complète | 12 | 0h-24h |
| Matinale | 4 | 8h-12h |
| Après-midi | 4 | 13h-17h |

## 🎲 Complexité du Problème

### Classe de Complexité

Le VRP est un problème **NP-difficile**, ce qui signifie :
- Pas d'algorithme polynomial connu pour trouver la solution optimale
- Le temps de calcul augmente exponentiellement avec le nombre de clients
- Pour n clients et k véhicules : O((n!)/((k!)^k)) possibilités

### Nombre de Solutions Possibles

Pour notre problème (20 clients, 3 véhicules) :
- Nombre approximatif de solutions : > 10^18
- Nécessité d'utiliser des heuristiques et métaheuristiques

### Pourquoi OR-Tools ?

**OR-Tools** de Google est choisi car :
1. Implémentation optimisée des algorithmes de routage
2. Gestion native des contraintes complexes
3. Métaheuristiques performantes (Guided Local Search)
4. Support des fenêtres horaires et capacités
5. Open source et bien documenté

## 🔄 Variantes du VRP

Notre implémentation gère plusieurs variantes :

1. **CVRP** (Capacitated VRP)
   - Contraintes de capacité des véhicules

2. **VRPTW** (VRP with Time Windows)
   - Fenêtres horaires de livraison

3. **VRP with Priorities**
   - Niveaux de priorité des clients

4. **VRP with Service Times**
   - Temps de service différencié par client

## 📊 Indicateurs de Performance

### Métriques Principales

1. **Distance Totale** : Somme des distances parcourues par tous les véhicules
2. **Taux de Service** : Pourcentage de clients servis
3. **Taux d'Utilisation** : Charge moyenne des véhicules / capacité
4. **Équilibrage** : Distribution de la charge entre véhicules

### Critères de Qualité d'une Solution

Une bonne solution doit :
- ✅ Servir 100% des clients (si possible)
- ✅ Respecter toutes les contraintes
- ✅ Minimiser la distance totale
- ✅ Équilibrer les charges entre véhicules
- ✅ Favoriser les clients haute priorité
- ✅ Optimiser le taux d'utilisation des véhicules

## 🌍 Applications Réelles

Le VRP est utilisé dans de nombreux domaines :

1. **Logistique** : Livraison de colis, distribution de marchandises
2. **Services** : Ramassage des déchets, maintenance, livraison de courrier
3. **Transport** : Planification de circuits de bus scolaires
4. **E-commerce** : Optimisation des livraisons du dernier kilomètre
5. **Santé** : Tournées des infirmières à domicile

## 🎯 Impact de l'Optimisation

### Bénéfices Attendus

1. **Économiques**
   - Réduction des coûts de carburant (20-30%)
   - Diminution des coûts de maintenance
   - Meilleure utilisation des ressources

2. **Opérationnels**
   - Temps de livraison réduits
   - Plus de clients servis
   - Planification prévisible

3. **Environnementaux**
   - Réduction des émissions de CO2
   - Diminution de l'empreinte carbone

4. **Service Client**
   - Respect des créneaux horaires
   - Fiabilité améliorée
   - Satisfaction client accrue

## 📖 Références

- **OR-Tools Documentation** : https://developers.google.com/optimization
- **VRP Theory** : Toth, P., & Vigo, D. (2014). Vehicle Routing: Problems, Methods, and Applications
- **Optimization Methods** : Clarke, G., & Wright, J. W. (1964). Scheduling of Vehicles from a Central Depot
