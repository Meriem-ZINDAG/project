"""
Module d'optimisation pour le problème VRP (Vehicle Routing Problem).
Utilise OR-Tools de Google pour résoudre le problème d'optimisation des tournées.
"""

import numpy as np
from typing import Dict, List, Tuple
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


class VRPOptimizer:
    """Classe pour optimiser les tournées de véhicules avec OR-Tools."""
    
    def __init__(self, data_handler, config: Dict):
        """
        Initialise l'optimiseur VRP.
        
        Args:
            data_handler: Instance de DataHandler contenant les données
            config: Configuration de l'optimisation
        """
        self.data_handler = data_handler
        self.config = config
        self.solution = None
        self.routing = None
        self.manager = None
        
    def create_data_model(self) -> Dict:
        """
        Crée le modèle de données pour OR-Tools.
        
        Returns:
            Dictionnaire contenant toutes les données nécessaires
        """
        data = {}
        
        # Matrice de distances (convertie en entiers pour OR-Tools)
        distance_matrix = self.data_handler.distance_matrix
        data['distance_matrix'] = (distance_matrix * 100).astype(int).tolist()
        
        # Demandes des clients
        data['demands'] = self.data_handler.get_demands()
        
        # Capacité des véhicules
        data['vehicle_capacities'] = [
            self.config['vehicle_capacity']
        ] * self.config['num_vehicles']
        
        # Fenêtres horaires
        time_windows = self.data_handler.get_time_windows()
        data['time_windows'] = time_windows
        
        # Temps de service
        data['service_times'] = self.data_handler.get_service_times()
        
        # Priorités
        data['priorities'] = self.data_handler.get_priorities()
        
        # Nombre de véhicules
        data['num_vehicles'] = self.config['num_vehicles']
        
        # Dépôt (toujours l'indice 0)
        data['depot'] = 0
        
        return data
    
    def solve(self) -> Dict:
        """
        Résout le problème VRP avec OR-Tools.
        
        Returns:
            Dictionnaire contenant la solution optimale
        """
        print("\n🔍 Résolution du problème VRP...")
        
        # Créer le modèle de données
        data = self.create_data_model()
        
        # Créer le gestionnaire d'indices
        self.manager = pywrapcp.RoutingIndexManager(
            len(data['distance_matrix']),
            data['num_vehicles'],
            data['depot']
        )
        
        # Créer le modèle de routage
        self.routing = pywrapcp.RoutingModel(self.manager)
        
        # Définir la fonction de coût (distance)
        def distance_callback(from_index, to_index):
            """Retourne la distance entre deux nœuds."""
            from_node = self.manager.IndexToNode(from_index)
            to_node = self.manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]
        
        transit_callback_index = self.routing.RegisterTransitCallback(distance_callback)
        self.routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Ajouter la contrainte de capacité
        def demand_callback(from_index):
            """Retourne la demande d'un nœud."""
            from_node = self.manager.IndexToNode(from_index)
            return data['demands'][from_node]
        
        demand_callback_index = self.routing.RegisterUnaryTransitCallback(demand_callback)
        self.routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # slack nul
            data['vehicle_capacities'],  # capacités des véhicules
            True,  # commencer à zéro
            'Capacity'
        )
        
        # Ajouter la dimension temporelle avec fenêtres horaires
        def time_callback(from_index, to_index):
            """Retourne le temps de trajet + temps de service."""
            from_node = self.manager.IndexToNode(from_index)
            to_node = self.manager.IndexToNode(to_index)
            travel_time = data['distance_matrix'][from_node][to_node]  # Distance = temps
            service_time = data['service_times'][from_node]
            return travel_time + service_time
        
        time_callback_index = self.routing.RegisterTransitCallback(time_callback)
        
        # Dimension temporelle
        time_dimension_name = 'Time'
        self.routing.AddDimension(
            time_callback_index,
            480,  # temps d'attente maximum (8 heures)
            1440,  # horizon temporel maximum (24 heures)
            False,  # ne pas forcer à commencer à zéro
            time_dimension_name
        )
        time_dimension = self.routing.GetDimensionOrDie(time_dimension_name)
        
        # Ajouter les contraintes de fenêtres horaires
        for location_idx, time_window in enumerate(data['time_windows']):
            if location_idx == data['depot']:
                continue
            index = self.manager.NodeToIndex(location_idx)
            time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
        
        # Définir les fenêtres horaires du dépôt pour tous les véhicules
        depot_idx = data['depot']
        for vehicle_id in range(data['num_vehicles']):
            index = self.routing.Start(vehicle_id)
            time_dimension.CumulVar(index).SetRange(
                data['time_windows'][depot_idx][0],
                data['time_windows'][depot_idx][1]
            )
        
        # Ajouter les pénalités de priorité (clients haute priorité favorisés)
        priority_penalty = int(self.config['weight_priority'] * 10000)
        for node in range(len(data['priorities'])):
            if node == data['depot']:
                continue
            index = self.manager.NodeToIndex(node)
            priority = data['priorities'][node]
            # Priorité 1 = haute (pénalité faible), 3 = basse (pénalité élevée)
            penalty = priority_penalty * priority
            self.routing.AddDisjunction([index], penalty)
        
        # Paramètres de recherche
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = self.config['time_limit']
        search_parameters.log_search = self.config.get('verbose', False)
        
        # Résoudre le problème
        print("  ⏳ Recherche de la solution optimale en cours...")
        self.solution = self.routing.SolveWithParameters(search_parameters)
        
        if self.solution:
            print("  ✓ Solution trouvée !")
            return self._extract_solution(data)
        else:
            print("  ❌ Aucune solution trouvée.")
            return None
    
    def _extract_solution(self, data: Dict) -> Dict:
        """
        Extrait les détails de la solution trouvée.
        
        Args:
            data: Modèle de données utilisé
        
        Returns:
            Dictionnaire contenant les détails de la solution
        """
        solution_dict = {
            'routes': [],
            'total_distance': 0,
            'total_load': 0,
            'total_time': 0,
            'vehicle_stats': []
        }
        
        time_dimension = self.routing.GetDimensionOrDie('Time')
        
        for vehicle_id in range(data['num_vehicles']):
            route = []
            route_distance = 0
            route_load = 0
            route_time = 0
            
            index = self.routing.Start(vehicle_id)
            route_info = []
            
            while not self.routing.IsEnd(index):
                node_index = self.manager.IndexToNode(index)
                route.append(node_index)
                
                # Informations détaillées du nœud
                time_var = time_dimension.CumulVar(index)
                arrival_time = self.solution.Min(time_var)
                
                route_info.append({
                    'node': node_index,
                    'nom': self.data_handler.clients_df.loc[node_index, 'nom'],
                    'demande': data['demands'][node_index],
                    'arrival_time': arrival_time,
                    'priority': data['priorities'][node_index]
                })
                
                route_load += data['demands'][node_index]
                
                # Distance au prochain nœud
                previous_index = index
                index = self.solution.Value(self.routing.NextVar(index))
                route_distance += self.routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )
            
            # Ajouter le retour au dépôt
            node_index = self.manager.IndexToNode(index)
            route.append(node_index)
            time_var = time_dimension.CumulVar(index)
            arrival_time = self.solution.Min(time_var)
            
            route_info.append({
                'node': node_index,
                'nom': self.data_handler.clients_df.loc[node_index, 'nom'],
                'demande': 0,
                'arrival_time': arrival_time,
                'priority': 0
            })
            
            # Convertir la distance en unités réelles (divisé par 100)
            route_distance_real = route_distance / 100.0
            
            # Ne garder que les routes non vides (qui visitent au moins un client)
            if len(route) > 2:  # Plus que dépôt -> dépôt
                solution_dict['routes'].append(route)
                solution_dict['vehicle_stats'].append({
                    'vehicle_id': vehicle_id,
                    'route': route,
                    'route_info': route_info,
                    'distance': route_distance_real,
                    'load': route_load,
                    'capacity_used': (route_load / data['vehicle_capacities'][vehicle_id]) * 100
                })
                
                solution_dict['total_distance'] += route_distance_real
                solution_dict['total_load'] += route_load
        
        # Coût objectif total
        solution_dict['objective_value'] = self.solution.ObjectiveValue() / 100.0
        
        return solution_dict
    
    def print_solution(self, solution: Dict):
        """
        Affiche la solution de manière formatée.
        
        Args:
            solution: Dictionnaire contenant la solution
        """
        print("\n" + "=" * 80)
        print("📊 RÉSULTATS DE L'OPTIMISATION")
        print("=" * 80)
        
        print(f"\n🎯 Distance totale optimale : {solution['total_distance']:.2f} unités")
        print(f"📦 Charge totale transportée : {solution['total_load']} unités")
        print(f"🚛 Nombre de véhicules utilisés : {len(solution['vehicle_stats'])}")
        
        print("\n" + "─" * 80)
        print("DÉTAILS DES TOURNÉES PAR VÉHICULE")
        print("─" * 80)
        
        for stats in solution['vehicle_stats']:
            print(f"\n🚛 Véhicule {stats['vehicle_id'] + 1}")
            print(f"   Distance parcourue : {stats['distance']:.2f} unités")
            print(f"   Charge transportée : {stats['load']} unités")
            print(f"   Taux d'utilisation : {stats['capacity_used']:.1f}%")
            print(f"   Itinéraire :")
            
            for i, info in enumerate(stats['route_info']):
                arrival_str = f"{info['arrival_time'] // 60:02d}h{info['arrival_time'] % 60:02d}"
                priority_str = ""
                if info['priority'] > 0:
                    priority_levels = {1: "⭐ Haute", 2: "🔶 Moyenne", 3: "🔵 Basse"}
                    priority_str = f" - Priorité: {priority_levels.get(info['priority'], '')}"
                
                if i == 0:
                    print(f"      {i}. [{arrival_str}] {info['nom']} (Départ)")
                elif i == len(stats['route_info']) - 1:
                    print(f"      {i}. [{arrival_str}] {info['nom']} (Retour)")
                else:
                    print(f"      {i}. [{arrival_str}] {info['nom']} - Demande: {info['demande']} unités{priority_str}")
        
        print("\n" + "=" * 80)
