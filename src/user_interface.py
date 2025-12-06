"""
Module d'interface utilisateur pour la configuration du problème VRP.
Permet la saisie interactive des paramètres d'optimisation.
"""

from typing import Dict, Tuple


class UserInterface:
    """Classe pour gérer l'interface utilisateur et la saisie des paramètres."""
    
    def __init__(self):
        """Initialise l'interface utilisateur."""
        self.config = {}
    
    def display_welcome(self):
        """Affiche le message de bienvenue."""
        print("=" * 80)
        print("  🚛 OPTIMISATION DE TOURNÉES DE LIVRAISON (VRP) 🚛")
        print("=" * 80)
        print("\nBienvenue dans le système d'optimisation de tournées de livraison.")
        print("Ce système utilise l'intelligence artificielle (OR-Tools de Google)")
        print("pour optimiser les tournées d'une flotte de véhicules.\n")
    
    def get_vehicle_parameters(self, interactive: bool = True) -> Dict:
        """
        Collecte les paramètres des véhicules auprès de l'utilisateur.
        
        Args:
            interactive: Si True, demande à l'utilisateur, sinon utilise les valeurs par défaut
        
        Returns:
            Dictionnaire contenant les paramètres des véhicules
        """
        print("\n" + "─" * 80)
        print("📋 CONFIGURATION DES VÉHICULES")
        print("─" * 80)
        
        if interactive:
            num_vehicles = self._get_int_input(
                "Nombre de véhicules disponibles",
                default=3,
                min_value=1,
                max_value=10
            )
            
            vehicle_capacity = self._get_int_input(
                "Capacité de chaque véhicule (unités)",
                default=50,
                min_value=10,
                max_value=200
            )
        else:
            num_vehicles = 3
            vehicle_capacity = 50
            print(f"Nombre de véhicules : {num_vehicles}")
            print(f"Capacité par véhicule : {vehicle_capacity} unités")
        
        self.config['num_vehicles'] = num_vehicles
        self.config['vehicle_capacity'] = vehicle_capacity
        
        return {
            'num_vehicles': num_vehicles,
            'vehicle_capacity': vehicle_capacity
        }
    
    def get_optimization_parameters(self, interactive: bool = True) -> Dict:
        """
        Collecte les paramètres d'optimisation auprès de l'utilisateur.
        
        Args:
            interactive: Si True, demande à l'utilisateur, sinon utilise les valeurs par défaut
        
        Returns:
            Dictionnaire contenant les paramètres d'optimisation
        """
        print("\n" + "─" * 80)
        print("⚙️  PARAMÈTRES D'OPTIMISATION")
        print("─" * 80)
        
        if interactive:
            print("\nPondérations pour l'optimisation :")
            print("  - Distance : minimise la distance totale parcourue")
            print("  - Priorité : favorise les clients à haute priorité")
            print("  - Temps : minimise le temps total de service\n")
            
            weight_distance = self._get_float_input(
                "Poids de la distance",
                default=1.0,
                min_value=0.0,
                max_value=10.0
            )
            
            weight_priority = self._get_float_input(
                "Poids de la priorité",
                default=0.5,
                min_value=0.0,
                max_value=10.0
            )
            
            weight_time = self._get_float_input(
                "Poids du temps",
                default=0.3,
                min_value=0.0,
                max_value=10.0
            )
            
            time_limit = self._get_int_input(
                "Temps limite de recherche (secondes)",
                default=30,
                min_value=5,
                max_value=300
            )
        else:
            weight_distance = 1.0
            weight_priority = 0.5
            weight_time = 0.3
            time_limit = 30
            print(f"Poids distance : {weight_distance}")
            print(f"Poids priorité : {weight_priority}")
            print(f"Poids temps : {weight_time}")
            print(f"Temps limite : {time_limit} secondes")
        
        self.config.update({
            'weight_distance': weight_distance,
            'weight_priority': weight_priority,
            'weight_time': weight_time,
            'time_limit': time_limit
        })
        
        return {
            'weight_distance': weight_distance,
            'weight_priority': weight_priority,
            'weight_time': weight_time,
            'time_limit': time_limit
        }
    
    def get_output_preferences(self, interactive: bool = True) -> Dict:
        """
        Collecte les préférences de sortie auprès de l'utilisateur.
        
        Args:
            interactive: Si True, demande à l'utilisateur, sinon utilise les valeurs par défaut
        
        Returns:
            Dictionnaire contenant les préférences de sortie
        """
        print("\n" + "─" * 80)
        print("📊 PRÉFÉRENCES DE SORTIE")
        print("─" * 80)
        
        if interactive:
            show_visualization = self._get_bool_input(
                "Afficher la visualisation graphique ?",
                default=True
            )
            
            save_results = self._get_bool_input(
                "Sauvegarder les résultats ?",
                default=True
            )
            
            verbose = self._get_bool_input(
                "Mode détaillé (verbose) ?",
                default=True
            )
        else:
            show_visualization = True
            save_results = True
            verbose = True
            print(f"Visualisation : {'Oui' if show_visualization else 'Non'}")
            print(f"Sauvegarde : {'Oui' if save_results else 'Non'}")
            print(f"Mode détaillé : {'Oui' if verbose else 'Non'}")
        
        self.config.update({
            'show_visualization': show_visualization,
            'save_results': save_results,
            'verbose': verbose
        })
        
        return {
            'show_visualization': show_visualization,
            'save_results': save_results,
            'verbose': verbose
        }
    
    def get_all_parameters(self, interactive: bool = True) -> Dict:
        """
        Collecte tous les paramètres nécessaires.
        
        Args:
            interactive: Si True, mode interactif, sinon utilise les valeurs par défaut
        
        Returns:
            Dictionnaire contenant tous les paramètres
        """
        self.display_welcome()
        
        vehicle_params = self.get_vehicle_parameters(interactive)
        optimization_params = self.get_optimization_parameters(interactive)
        output_params = self.get_output_preferences(interactive)
        
        all_params = {
            **vehicle_params,
            **optimization_params,
            **output_params
        }
        
        if interactive:
            print("\n" + "─" * 80)
            self._confirm_parameters(all_params)
        
        return all_params
    
    def _get_int_input(self, prompt: str, default: int, min_value: int, max_value: int) -> int:
        """
        Demande une valeur entière à l'utilisateur avec validation.
        
        Args:
            prompt: Message à afficher
            default: Valeur par défaut
            min_value: Valeur minimale acceptée
            max_value: Valeur maximale acceptée
        
        Returns:
            Valeur entière saisie
        """
        while True:
            try:
                user_input = input(f"{prompt} [défaut: {default}] : ").strip()
                if not user_input:
                    return default
                
                value = int(user_input)
                if min_value <= value <= max_value:
                    return value
                else:
                    print(f"  ⚠️  Valeur hors limites. Entrez une valeur entre {min_value} et {max_value}.")
            except ValueError:
                print(f"  ⚠️  Entrée invalide. Entrez un nombre entier.")
    
    def _get_float_input(self, prompt: str, default: float, min_value: float, max_value: float) -> float:
        """
        Demande une valeur décimale à l'utilisateur avec validation.
        
        Args:
            prompt: Message à afficher
            default: Valeur par défaut
            min_value: Valeur minimale acceptée
            max_value: Valeur maximale acceptée
        
        Returns:
            Valeur décimale saisie
        """
        while True:
            try:
                user_input = input(f"{prompt} [défaut: {default}] : ").strip()
                if not user_input:
                    return default
                
                value = float(user_input)
                if min_value <= value <= max_value:
                    return value
                else:
                    print(f"  ⚠️  Valeur hors limites. Entrez une valeur entre {min_value} et {max_value}.")
            except ValueError:
                print(f"  ⚠️  Entrée invalide. Entrez un nombre décimal.")
    
    def _get_bool_input(self, prompt: str, default: bool) -> bool:
        """
        Demande une valeur booléenne à l'utilisateur.
        
        Args:
            prompt: Message à afficher
            default: Valeur par défaut
        
        Returns:
            Valeur booléenne saisie
        """
        default_str = "O" if default else "N"
        while True:
            user_input = input(f"{prompt} [O/N, défaut: {default_str}] : ").strip().upper()
            if not user_input:
                return default
            if user_input in ['O', 'OUI', 'Y', 'YES']:
                return True
            elif user_input in ['N', 'NON', 'NO']:
                return False
            else:
                print("  ⚠️  Entrée invalide. Entrez O (oui) ou N (non).")
    
    def _confirm_parameters(self, params: Dict):
        """
        Affiche un récapitulatif des paramètres et demande confirmation.
        
        Args:
            params: Dictionnaire des paramètres
        """
        print("\n✓ Configuration terminée. Récapitulatif :")
        print(f"  • Véhicules : {params['num_vehicles']}")
        print(f"  • Capacité : {params['vehicle_capacity']} unités")
        print(f"  • Poids distance : {params['weight_distance']}")
        print(f"  • Poids priorité : {params['weight_priority']}")
        print(f"  • Poids temps : {params['weight_time']}")
        print(f"  • Temps limite : {params['time_limit']} secondes")
        print("─" * 80)
    
    def display_progress(self, message: str):
        """
        Affiche un message de progression.
        
        Args:
            message: Message à afficher
        """
        print(f"\n🔄 {message}...")
    
    def display_success(self, message: str):
        """
        Affiche un message de succès.
        
        Args:
            message: Message à afficher
        """
        print(f"\n✓ {message}")
    
    def display_error(self, message: str):
        """
        Affiche un message d'erreur.
        
        Args:
            message: Message à afficher
        """
        print(f"\n❌ Erreur : {message}")
