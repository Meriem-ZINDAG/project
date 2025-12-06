"""
Module d'analyse des résultats pour le problème VRP.
Calcule des métriques et fournit des insights sur la solution optimisée.
"""

import numpy as np
from typing import Dict, List, Tuple
import json
import os


class VRPAnalyzer:
    """Classe pour analyser les résultats de l'optimisation VRP."""
    
    def __init__(self, data_handler, solution: Dict, config: Dict):
        """
        Initialise l'analyseur.
        
        Args:
            data_handler: Instance de DataHandler contenant les données
            solution: Dictionnaire contenant la solution optimisée
            config: Configuration utilisée pour l'optimisation
        """
        self.data_handler = data_handler
        self.solution = solution
        self.config = config
        self.metrics = {}
    
    def calculate_metrics(self) -> Dict:
        """
        Calcule toutes les métriques de performance.
        
        Returns:
            Dictionnaire contenant les métriques calculées
        """
        print("\n📈 Analyse des résultats...")
        
        self.metrics = {
            'total_distance': self.solution['total_distance'],
            'total_load': self.solution['total_load'],
            'num_vehicles_used': len(self.solution['vehicle_stats']),
            'num_vehicles_available': self.config['num_vehicles'],
            'vehicle_capacity': self.config['vehicle_capacity']
        }
        
        # Distance moyenne par véhicule
        distances = [stats['distance'] for stats in self.solution['vehicle_stats']]
        self.metrics['avg_distance_per_vehicle'] = np.mean(distances)
        self.metrics['max_distance'] = max(distances)
        self.metrics['min_distance'] = min(distances)
        
        # Charge moyenne par véhicule
        loads = [stats['load'] for stats in self.solution['vehicle_stats']]
        self.metrics['avg_load_per_vehicle'] = np.mean(loads)
        self.metrics['max_load'] = max(loads)
        self.metrics['min_load'] = min(loads)
        
        # Taux d'utilisation moyen
        capacity_used = [stats['capacity_used'] for stats in self.solution['vehicle_stats']]
        self.metrics['avg_capacity_used'] = np.mean(capacity_used)
        
        # Équilibrage de la charge
        self.metrics['load_balance'] = self._calculate_load_balance(loads)
        
        # Distance balance
        self.metrics['distance_balance'] = self._calculate_distance_balance(distances)
        
        # Nombre de clients servis
        total_clients = len(self.data_handler.clients_df) - 1  # Exclure le dépôt
        clients_served = sum(len(route) - 2 for route in self.solution['routes'])  # -2 pour les deux dépôts
        self.metrics['clients_served'] = clients_served
        self.metrics['total_clients'] = total_clients
        self.metrics['service_rate'] = (clients_served / total_clients) * 100
        
        # Véhicule le plus chargé
        busiest_vehicle = self._find_busiest_vehicle()
        self.metrics['busiest_vehicle'] = busiest_vehicle
        
        # Statistiques sur les priorités
        priority_stats = self._analyze_priorities()
        self.metrics['priority_stats'] = priority_stats
        
        return self.metrics
    
    def _calculate_load_balance(self, loads: List[int]) -> float:
        """
        Calcule l'équilibrage de la charge entre les véhicules.
        
        Args:
            loads: Liste des charges par véhicule
        
        Returns:
            Score d'équilibrage (0-100, 100 = parfaitement équilibré)
        """
        if len(loads) <= 1:
            return 100.0
        
        mean_load = np.mean(loads)
        if mean_load == 0:
            return 100.0
        
        std_load = np.std(loads)
        coefficient_variation = (std_load / mean_load) * 100
        
        # Convertir en score (plus le CV est bas, meilleur est l'équilibrage)
        balance_score = max(0, 100 - coefficient_variation)
        return balance_score
    
    def _calculate_distance_balance(self, distances: List[float]) -> float:
        """
        Calcule l'équilibrage des distances entre les véhicules.
        
        Args:
            distances: Liste des distances par véhicule
        
        Returns:
            Score d'équilibrage (0-100, 100 = parfaitement équilibré)
        """
        if len(distances) <= 1:
            return 100.0
        
        mean_distance = np.mean(distances)
        if mean_distance == 0:
            return 100.0
        
        std_distance = np.std(distances)
        coefficient_variation = (std_distance / mean_distance) * 100
        
        balance_score = max(0, 100 - coefficient_variation)
        return balance_score
    
    def _find_busiest_vehicle(self) -> Dict:
        """
        Identifie le véhicule le plus chargé.
        
        Returns:
            Dictionnaire avec les informations du véhicule le plus chargé
        """
        busiest = max(self.solution['vehicle_stats'], 
                     key=lambda x: (x['load'], x['distance']))
        
        return {
            'vehicle_id': busiest['vehicle_id'],
            'distance': busiest['distance'],
            'load': busiest['load'],
            'capacity_used': busiest['capacity_used'],
            'num_clients': len(busiest['route']) - 2  # Exclure les deux passages au dépôt
        }
    
    def _analyze_priorities(self) -> Dict:
        """
        Analyse la distribution des priorités dans les tournées.
        
        Returns:
            Dictionnaire avec les statistiques sur les priorités
        """
        priority_count = {1: 0, 2: 0, 3: 0}
        priority_served = {1: 0, 2: 0, 3: 0}
        
        # Compter toutes les priorités
        for i in range(1, len(self.data_handler.clients_df)):
            priority = self.data_handler.clients_df.loc[i, 'priorite']
            priority_count[priority] += 1
        
        # Compter les priorités servies
        for stats in self.solution['vehicle_stats']:
            for info in stats['route_info']:
                if info['priority'] > 0:
                    priority_served[info['priority']] += 1
        
        return {
            'high_priority': {
                'total': priority_count[1],
                'served': priority_served[1],
                'rate': (priority_served[1] / priority_count[1] * 100) if priority_count[1] > 0 else 0
            },
            'medium_priority': {
                'total': priority_count[2],
                'served': priority_served[2],
                'rate': (priority_served[2] / priority_count[2] * 100) if priority_count[2] > 0 else 0
            },
            'low_priority': {
                'total': priority_count[3],
                'served': priority_served[3],
                'rate': (priority_served[3] / priority_count[3] * 100) if priority_count[3] > 0 else 0
            }
        }
    
    def print_analysis(self):
        """Affiche l'analyse détaillée des résultats."""
        print("\n" + "=" * 80)
        print("📊 ANALYSE DÉTAILLÉE DES RÉSULTATS")
        print("=" * 80)
        
        print("\n📍 MÉTRIQUES GÉNÉRALES")
        print(f"  • Distance totale : {self.metrics['total_distance']:.2f} unités")
        print(f"  • Charge totale : {self.metrics['total_load']} unités")
        print(f"  • Véhicules utilisés : {self.metrics['num_vehicles_used']} / {self.metrics['num_vehicles_available']}")
        print(f"  • Clients servis : {self.metrics['clients_served']} / {self.metrics['total_clients']} ({self.metrics['service_rate']:.1f}%)")
        
        print("\n📏 DISTRIBUTION DES DISTANCES")
        print(f"  • Distance moyenne par véhicule : {self.metrics['avg_distance_per_vehicle']:.2f} unités")
        print(f"  • Distance maximale : {self.metrics['max_distance']:.2f} unités")
        print(f"  • Distance minimale : {self.metrics['min_distance']:.2f} unités")
        print(f"  • Équilibrage des distances : {self.metrics['distance_balance']:.1f}/100")
        
        print("\n📦 DISTRIBUTION DES CHARGES")
        print(f"  • Charge moyenne par véhicule : {self.metrics['avg_load_per_vehicle']:.1f} unités")
        print(f"  • Charge maximale : {self.metrics['max_load']} unités")
        print(f"  • Charge minimale : {self.metrics['min_load']} unités")
        print(f"  • Taux d'utilisation moyen : {self.metrics['avg_capacity_used']:.1f}%")
        print(f"  • Équilibrage des charges : {self.metrics['load_balance']:.1f}/100")
        
        print("\n🚛 VÉHICULE LE PLUS CHARGÉ")
        busiest = self.metrics['busiest_vehicle']
        print(f"  • Véhicule n°{busiest['vehicle_id'] + 1}")
        print(f"  • Distance : {busiest['distance']:.2f} unités")
        print(f"  • Charge : {busiest['load']} unités ({busiest['capacity_used']:.1f}%)")
        print(f"  • Nombre de clients : {busiest['num_clients']}")
        
        print("\n⭐ ANALYSE DES PRIORITÉS")
        pstats = self.metrics['priority_stats']
        print(f"  • Priorité Haute (1) : {pstats['high_priority']['served']}/{pstats['high_priority']['total']} " +
              f"({pstats['high_priority']['rate']:.1f}%)")
        print(f"  • Priorité Moyenne (2) : {pstats['medium_priority']['served']}/{pstats['medium_priority']['total']} " +
              f"({pstats['medium_priority']['rate']:.1f}%)")
        print(f"  • Priorité Basse (3) : {pstats['low_priority']['served']}/{pstats['low_priority']['total']} " +
              f"({pstats['low_priority']['rate']:.1f}%)")
    
    def generate_recommendations(self) -> List[str]:
        """
        Génère des recommandations basées sur l'analyse.
        
        Returns:
            Liste de recommandations
        """
        recommendations = []
        
        # Utilisation des véhicules
        if self.metrics['num_vehicles_used'] < self.metrics['num_vehicles_available']:
            unused = self.metrics['num_vehicles_available'] - self.metrics['num_vehicles_used']
            recommendations.append(
                f"💡 {unused} véhicule(s) non utilisé(s). Vous pourriez réduire la flotte pour optimiser les coûts."
            )
        
        # Taux d'utilisation faible
        if self.metrics['avg_capacity_used'] < 60:
            recommendations.append(
                f"💡 Taux d'utilisation moyen faible ({self.metrics['avg_capacity_used']:.1f}%). " +
                "Envisagez de réduire la capacité des véhicules ou d'augmenter le nombre de clients par tournée."
            )
        
        # Mauvais équilibrage
        if self.metrics['load_balance'] < 70:
            recommendations.append(
                f"💡 Équilibrage des charges peu optimal ({self.metrics['load_balance']:.1f}/100). " +
                "Ajustez les poids d'optimisation pour mieux équilibrer la charge entre les véhicules."
            )
        
        if self.metrics['distance_balance'] < 70:
            recommendations.append(
                f"💡 Équilibrage des distances peu optimal ({self.metrics['distance_balance']:.1f}/100). " +
                "Certains véhicules parcourent des distances très différentes."
            )
        
        # Clients non servis
        if self.metrics['service_rate'] < 100:
            unserved = self.metrics['total_clients'] - self.metrics['clients_served']
            recommendations.append(
                f"⚠️  {unserved} client(s) non servi(s). Augmentez le nombre de véhicules ou leur capacité."
            )
        
        # Priorités non servies
        pstats = self.metrics['priority_stats']
        if pstats['high_priority']['rate'] < 100:
            recommendations.append(
                f"⚠️  Certains clients haute priorité ne sont pas servis. " +
                "Augmentez le poids de la priorité dans les paramètres d'optimisation."
            )
        
        # Bonne performance
        if (self.metrics['service_rate'] == 100 and 
            self.metrics['load_balance'] >= 80 and 
            self.metrics['distance_balance'] >= 80):
            recommendations.append(
                "✅ Excellente solution ! Les tournées sont bien équilibrées et tous les clients sont servis."
            )
        
        return recommendations
    
    def print_recommendations(self):
        """Affiche les recommandations."""
        recommendations = self.generate_recommendations()
        
        if recommendations:
            print("\n" + "=" * 80)
            print("💡 RECOMMANDATIONS ET SUGGESTIONS D'AMÉLIORATION")
            print("=" * 80)
            for rec in recommendations:
                print(f"\n{rec}")
        
        print("\n" + "=" * 80)
    
    def export_results(self, output_dir: str = 'output', filename: str = 'vrp_analysis.json'):
        """
        Exporte les résultats de l'analyse au format JSON.
        
        Args:
            output_dir: Dossier de sortie
            filename: Nom du fichier
        """
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        export_data = {
            'configuration': self.config,
            'solution': {
                'total_distance': self.solution['total_distance'],
                'total_load': self.solution['total_load'],
                'vehicle_stats': self.solution['vehicle_stats']
            },
            'metrics': self.metrics,
            'recommendations': self.generate_recommendations()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Résultats exportés vers : {filepath}")
    
    def compare_with_baseline(self) -> Dict:
        """
        Compare la solution avec une solution de base (non optimisée).
        
        Returns:
            Dictionnaire contenant la comparaison
        """
        # Distance de base : si chaque véhicule fait un aller-retour simple
        num_clients = len(self.data_handler.clients_df) - 1
        avg_distance_to_depot = np.mean([
            self.data_handler.distance_matrix[0][i] 
            for i in range(1, len(self.data_handler.distance_matrix))
        ])
        
        baseline_distance = 2 * num_clients * avg_distance_to_depot
        improvement = ((baseline_distance - self.metrics['total_distance']) / baseline_distance) * 100
        
        return {
            'baseline_distance': baseline_distance,
            'optimized_distance': self.metrics['total_distance'],
            'improvement_percentage': improvement,
            'distance_saved': baseline_distance - self.metrics['total_distance']
        }
    
    def print_comparison(self):
        """Affiche la comparaison avec la solution de base."""
        comparison = self.compare_with_baseline()
        
        print("\n" + "=" * 80)
        print("📊 COMPARAISON AVEC SOLUTION NON OPTIMISÉE")
        print("=" * 80)
        print(f"\n  • Distance non optimisée : {comparison['baseline_distance']:.2f} unités")
        print(f"  • Distance optimisée : {comparison['optimized_distance']:.2f} unités")
        print(f"  • Économie de distance : {comparison['distance_saved']:.2f} unités ({comparison['improvement_percentage']:.1f}%)")
        print("\n" + "=" * 80)
