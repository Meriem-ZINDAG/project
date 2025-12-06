# Partie 2 : Modélisation Mathématique du VRP

## 🧮 Formulation Mathématique

### Ensembles et Indices

- **N** = {0, 1, 2, ..., n} : Ensemble des nœuds (0 = dépôt, 1..n = clients)
- **C** = {1, 2, ..., n} : Ensemble des clients (N \ {0})
- **K** = {1, 2, ..., k} : Ensemble des véhicules
- **A** = {(i,j) : i,j ∈ N, i ≠ j} : Ensemble des arcs

### Paramètres du Modèle

#### Distances et Temps
- **d<sub>ij</sub>** : Distance entre le nœud i et le nœud j
  - Calculée par distance euclidienne : d<sub>ij</sub> = √[(x<sub>i</sub> - x<sub>j</sub>)² + (y<sub>i</sub> - y<sub>j</sub>)²]
  - Matrice symétrique : d<sub>ij</sub> = d<sub>ji</sub>

#### Demandes
- **q<sub>i</sub>** : Demande du client i (en unités)
  - q<sub>0</sub> = 0 (le dépôt n'a pas de demande)
  - q<sub>i</sub> > 0 pour i ∈ C

#### Capacités
- **Q<sub>k</sub>** : Capacité du véhicule k
  - Dans notre cas : Q<sub>k</sub> = Q (capacité identique pour tous)

#### Fenêtres Horaires
- **[a<sub>i</sub>, b<sub>i</sub>]** : Fenêtre horaire du nœud i
  - a<sub>i</sub> : Heure de début de service la plus tôt
  - b<sub>i</sub> : Heure de début de service la plus tard

#### Temps de Service
- **s<sub>i</sub>** : Temps de service au nœud i (en minutes)

#### Priorités
- **p<sub>i</sub>** : Priorité du client i
  - p<sub>i</sub> ∈ {1, 2, 3} où 1 = haute, 2 = moyenne, 3 = basse

#### Poids d'Optimisation
- **w<sub>d</sub>** : Poids pour la distance
- **w<sub>p</sub>** : Poids pour la priorité
- **w<sub>t</sub>** : Poids pour le temps

### Variables de Décision

#### Variables Binaires de Routage
- **x<sub>ijk</sub>** ∈ {0, 1} : 
  - x<sub>ijk</sub> = 1 si le véhicule k traverse l'arc (i,j)
  - x<sub>ijk</sub> = 0 sinon

#### Variables de Temps
- **t<sub>ik</sub>** ≥ 0 : Heure de début de service au nœud i par le véhicule k

#### Variables de Charge
- **u<sub>ik</sub>** ≥ 0 : Charge cumulée du véhicule k après avoir visité le nœud i

## 🎯 Fonction Objectif

### Objectif Principal : Minimisation de la Distance Totale

```
Minimiser Z = Σ Σ Σ d_ij × x_ijk
              i∈N j∈N k∈K
```

### Objectif Multi-Critères (avec pondérations)

```
Minimiser Z = w_d × Σ Σ Σ d_ij × x_ijk  +  w_p × Σ p_i × (1 - Σ Σ x_ijk)
                    i∈N j∈N k∈K                 i∈C      k∈K j∈N
```

**Composantes** :
1. **Terme de distance** : Minimise la distance totale parcourue
2. **Terme de priorité** : Pénalise les clients non servis selon leur priorité

## 📐 Contraintes

### 1. Contraintes de Visite des Clients

#### Chaque client est visité exactement une fois
```
Σ Σ x_ijk = 1,  ∀i ∈ C
k∈K j∈N
```

#### Conservation du flux (ce qui entre doit sortir)
```
Σ x_ihk - Σ x_hjk = 0,  ∀h ∈ N, ∀k ∈ K
i∈N       j∈N
```

### 2. Contraintes de Capacité

#### La charge totale d'un véhicule ne dépasse pas sa capacité
```
Σ q_i × Σ x_ijk ≤ Q_k,  ∀k ∈ K
i∈C      j∈N
```

#### Contrainte de continuité de charge (sous-tour elimination)
```
u_ik - u_jk + Q_k × x_ijk ≤ Q_k - q_j,  ∀i,j ∈ C, i≠j, ∀k ∈ K
```

### 3. Contraintes de Fenêtres Horaires

#### Le service doit commencer dans la fenêtre horaire
```
a_i ≤ t_ik ≤ b_i,  ∀i ∈ N, ∀k ∈ K si le nœud i est visité par k
```

#### Contrainte de temps entre deux nœuds
```
t_ik + s_i + d_ij/v ≤ t_jk + M(1 - x_ijk),  ∀i,j ∈ N, ∀k ∈ K
```

où :
- M est une constante suffisamment grande (big M)
- v est la vitesse du véhicule (supposée = 1 pour notre modèle)

### 4. Contraintes sur les Véhicules

#### Chaque véhicule part du dépôt au plus une fois
```
Σ x_0jk ≤ 1,  ∀k ∈ K
j∈C
```

#### Chaque véhicule retourne au dépôt
```
Σ x_i0k = Σ x_0jk,  ∀k ∈ K
i∈C       j∈C
```

### 5. Contraintes de Non-Négativité et de Binarité

```
x_ijk ∈ {0, 1},  ∀i,j ∈ N, ∀k ∈ K
t_ik ≥ 0,  ∀i ∈ N, ∀k ∈ K
u_ik ≥ 0,  ∀i ∈ N, ∀k ∈ K
```

## 🔧 Implémentation avec OR-Tools

### Architecture du Solveur

OR-Tools utilise une approche de **Constraint Programming** combinée à des **métaheuristiques** :

#### 1. Création du Modèle de Routage

```python
manager = pywrapcp.RoutingIndexManager(
    len(locations),  # Nombre de nœuds
    num_vehicles,    # Nombre de véhicules
    depot           # Indice du dépôt
)

routing = pywrapcp.RoutingModel(manager)
```

#### 2. Fonction de Coût (Distance)

```python
def distance_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return distance_matrix[from_node][to_node]

transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
```

#### 3. Dimension de Capacité

```python
def demand_callback(from_index):
    from_node = manager.IndexToNode(from_index)
    return demands[from_node]

demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
routing.AddDimensionWithVehicleCapacity(
    demand_callback_index,
    0,                    # slack nul
    vehicle_capacities,   # capacités par véhicule
    True,                 # commencer à zéro
    'Capacity'
)
```

#### 4. Dimension Temporelle

```python
def time_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return distance_matrix[from_node][to_node] + service_times[from_node]

time_callback_index = routing.RegisterTransitCallback(time_callback)
routing.AddDimension(
    time_callback_index,
    480,                  # temps d'attente max
    1440,                 # horizon temporel
    False,                # ne pas forcer à commencer à zéro
    'Time'
)
```

#### 5. Fenêtres Horaires

```python
time_dimension = routing.GetDimensionOrDie('Time')
for location_idx, time_window in enumerate(time_windows):
    if location_idx == depot:
        continue
    index = manager.NodeToIndex(location_idx)
    time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
```

#### 6. Priorités (Disjonctions avec Pénalités)

```python
for node in range(len(priorities)):
    if node == depot:
        continue
    index = manager.NodeToIndex(node)
    priority = priorities[node]
    penalty = priority_weight * priority * 10000
    routing.AddDisjunction([index], penalty)
```

### Stratégies de Recherche

#### Solution Initiale
```python
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
)
```

**Options disponibles** :
- `PATH_CHEAPEST_ARC` : Construction gloutonne par arc le moins coûteux
- `SAVINGS` : Algorithme de savings de Clarke-Wright
- `CHRISTOFIDES` : Heuristique de Christofides
- `PARALLEL_CHEAPEST_INSERTION` : Insertion parallèle la moins coûteuse

#### Métaheuristique Locale
```python
search_parameters.local_search_metaheuristic = (
    routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
)
```

**Métaheuristiques disponibles** :
- `GUIDED_LOCAL_SEARCH` : Recherche locale guidée (recommandé)
- `SIMULATED_ANNEALING` : Recuit simulé
- `TABU_SEARCH` : Recherche tabou
- `GENETIC_ALGORITHM` : Algorithme génétique

## 📊 Complexité Algorithmique

### Complexité Temporelle

- **Construction solution initiale** : O(n²)
- **Recherche locale** : O(n² × k × t) où t = temps limite
- **Évaluation d'une solution** : O(n × k)

### Complexité Spatiale

- **Matrice de distances** : O(n²)
- **Variables de décision** : O(n × k)
- **Contraintes** : O(n × k)

## 🎲 Paramètres de Réglage

### Poids d'Optimisation

#### Impact des Poids

1. **w<sub>d</sub> (Distance)** :
   - Valeur élevée → Solutions compactes, distance minimale
   - Valeur faible → Plus de flexibilité pour autres objectifs

2. **w<sub>p</sub> (Priorité)** :
   - Valeur élevée → Favorise les clients haute priorité
   - Valeur faible → Traitement plus égalitaire

3. **w<sub>t</sub> (Temps)** :
   - Valeur élevée → Minimise le temps total
   - Valeur faible → Plus de temps d'attente acceptable

### Recommandations

| Scénario | w<sub>d</sub> | w<sub>p</sub> | w<sub>t</sub> |
|----------|---------------|---------------|---------------|
| Coût minimal | 1.0 | 0.3 | 0.2 |
| Service prioritaire | 0.5 | 1.0 | 0.3 |
| Équilibré (défaut) | 1.0 | 0.5 | 0.3 |
| Rapidité | 0.7 | 0.4 | 1.0 |

## 🔍 Validation du Modèle

### Tests de Cohérence

1. **Conservation du flux** : 
   - Vérifier que chaque véhicule qui quitte le dépôt y retourne

2. **Capacité** :
   - Somme des demandes ≤ Capacité pour chaque tournée

3. **Fenêtres horaires** :
   - Temps d'arrivée ∈ [a<sub>i</sub>, b<sub>i</sub>] pour chaque client

4. **Continuité** :
   - Pas de sous-tours isolés du dépôt

### Métriques de Qualité

1. **Optimality Gap** : Écart avec la borne inférieure
2. **Computation Time** : Temps de résolution
3. **Feasibility** : Respect de toutes les contraintes

## 📚 Références Mathématiques

### Articles Fondateurs

1. **Dantzig, G. B., & Ramser, J. H. (1959)**
   - "The Truck Dispatching Problem"
   - Management Science, 6(1), 80-91

2. **Clarke, G., & Wright, J. W. (1964)**
   - "Scheduling of Vehicles from a Central Depot to a Number of Delivery Points"
   - Operations Research, 12(4), 568-581

3. **Laporte, G. (2009)**
   - "Fifty Years of Vehicle Routing"
   - Transportation Science, 43(4), 408-416

### Ressources OR-Tools

- **Documentation officielle** : https://developers.google.com/optimization/routing
- **Guide VRP** : https://developers.google.com/optimization/routing/vrp
- **API Reference** : https://developers.google.com/optimization/reference/python/routing

## 🔗 Extensions Possibles

### Variantes Avancées

1. **VRPPD** : VRP with Pickup and Delivery
2. **MDVRP** : Multi-Depot VRP
3. **VRPB** : VRP with Backhauls
4. **PVRP** : Periodic VRP
5. **SDVRP** : Split Delivery VRP

### Améliorations du Modèle

1. Coûts asymétriques (aller ≠ retour)
2. Véhicules hétérogènes (capacités différentes)
3. Multiples dépôts
4. Pauses obligatoires pour conducteurs
5. Routes avec rechargement
