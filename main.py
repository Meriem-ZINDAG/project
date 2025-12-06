"""
Point d'entrée principal pour le projet d'optimisation VRP.
Orchestre l'ensemble du processus d'optimisation des tournées de livraison.
"""

import sys
import os

# Ajouter le dossier src au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_handler import DataHandler, get_default_clients_data
from user_interface import UserInterface
from optimizer import VRPOptimizer
from visualizer import VRPVisualizer
from analyzer import VRPAnalyzer


def main(interactive=True):
    """
    Fonction principale pour exécuter l'optimisation VRP.
    
    Args:
        interactive: Si True, demande les paramètres à l'utilisateur, sinon utilise les valeurs par défaut
    """
    try:
        # Étape 1: Interface utilisateur
        ui = UserInterface()
        
        # Récupérer les paramètres
        if interactive:
            config = ui.get_all_parameters(interactive=True)
        else:
            ui.display_welcome()
            config = ui.get_all_parameters(interactive=False)
        
        # Étape 2: Charger les données
        ui.display_progress("Chargement des données")
        data_handler = DataHandler()
        clients_data = get_default_clients_data()
        data_handler.load_clients_data(clients_data)
        data_handler.calculate_distance_matrix()
        
        # Étape 3: Optimisation
        ui.display_progress("Optimisation des tournées en cours")
        optimizer = VRPOptimizer(data_handler, config)
        solution = optimizer.solve()
        
        if not solution:
            ui.display_error("Aucune solution trouvée. Essayez d'ajuster les paramètres.")
            return False
        
        # Afficher la solution
        optimizer.print_solution(solution)
        
        # Étape 4: Analyse des résultats
        ui.display_progress("Analyse des résultats")
        analyzer = VRPAnalyzer(data_handler, solution, config)
        analyzer.calculate_metrics()
        analyzer.print_analysis()
        analyzer.print_comparison()
        analyzer.print_recommendations()
        
        # Étape 5: Visualisation
        if config.get('show_visualization', True):
            ui.display_progress("Génération des visualisations")
            visualizer = VRPVisualizer(data_handler)
            
            if config.get('save_results', True):
                # Sauvegarder toutes les visualisations
                visualizer.create_all_visualizations(solution, output_dir='output')
                
                # Afficher une visualisation interactive
                print("\n📊 Affichage de la visualisation interactive...")
                visualizer.plot_routes(solution, save_path=None, show=True)
            else:
                # Afficher seulement
                visualizer.plot_routes(solution, save_path=None, show=True)
        
        # Étape 6: Exporter les résultats
        if config.get('save_results', True):
            ui.display_progress("Export des résultats")
            analyzer.export_results(output_dir='output', filename='vrp_analysis.json')
            data_handler.export_to_csv('output/clients_data.csv')
        
        ui.display_success("Optimisation terminée avec succès!")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Opération annulée par l'utilisateur.")
        return False
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        return False


def main_non_interactive():
    """Lance l'optimisation en mode non-interactif avec les paramètres par défaut."""
    print("\n🤖 MODE NON-INTERACTIF")
    print("Utilisation des paramètres par défaut...\n")
    return main(interactive=False)


def display_menu():
    """Affiche le menu principal."""
    print("\n" + "=" * 80)
    print("  🚛 SYSTÈME D'OPTIMISATION DE TOURNÉES VRP 🚛")
    print("=" * 80)
    print("\nOptions disponibles:")
    print("  1. Lancer l'optimisation (mode interactif)")
    print("  2. Lancer l'optimisation (mode automatique)")
    print("  3. Démarrer le serveur API Flask")
    print("  4. Afficher l'aide")
    print("  5. Quitter")
    print("\n" + "─" * 80)
    
    choice = input("Votre choix [1-5] : ").strip()
    return choice


def display_help():
    """Affiche l'aide."""
    print("\n" + "=" * 80)
    print("  📖 AIDE - SYSTÈME D'OPTIMISATION VRP")
    print("=" * 80)
    print("\n📋 DESCRIPTION")
    print("  Ce système optimise les tournées de livraison pour une flotte de véhicules")
    print("  en utilisant OR-Tools de Google. Il prend en compte:")
    print("    • Les capacités des véhicules")
    print("    • Les fenêtres horaires de livraison")
    print("    • Les priorités des clients")
    print("    • Les distances entre les points")
    
    print("\n🎯 MODES D'UTILISATION")
    print("  1. Mode interactif : Vous saisissez les paramètres manuellement")
    print("  2. Mode automatique : Utilise les paramètres par défaut")
    print("  3. Mode API : Exposé via une API REST Flask")
    
    print("\n📊 SORTIES")
    print("  • Visualisations graphiques (PNG)")
    print("  • Fichier d'analyse (JSON)")
    print("  • Données des clients (CSV)")
    print("  • Affichage console détaillé")
    
    print("\n🔧 CONFIGURATION")
    print("  Paramètres modifiables:")
    print("    • Nombre de véhicules")
    print("    • Capacité des véhicules")
    print("    • Poids de la distance, priorité, temps")
    print("    • Temps limite de recherche")
    
    print("\n📁 STRUCTURE DES FICHIERS")
    print("  • src/ : Code source Python")
    print("  • docs/ : Documentation")
    print("  • output/ : Résultats et visualisations")
    print("  • n8n/ : Workflow d'automatisation")
    
    print("\n" + "=" * 80)


def start_api_server():
    """Démarre le serveur API Flask."""
    from api_server import run_server
    run_server(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    # Vérifier les arguments de ligne de commande
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'auto' or command == '--auto':
            # Mode automatique
            main_non_interactive()
        elif command == 'api' or command == '--api':
            # Mode API
            start_api_server()
        elif command == 'help' or command == '--help':
            # Aide
            display_help()
        else:
            print(f"❌ Commande inconnue : {command}")
            print("Utilisez 'python main.py help' pour afficher l'aide")
    else:
        # Menu interactif
        while True:
            choice = display_menu()
            
            if choice == '1':
                main(interactive=True)
                input("\nAppuyez sur Entrée pour continuer...")
            elif choice == '2':
                main_non_interactive()
                input("\nAppuyez sur Entrée pour continuer...")
            elif choice == '3':
                start_api_server()
                break
            elif choice == '4':
                display_help()
                input("\nAppuyez sur Entrée pour continuer...")
            elif choice == '5':
                print("\n👋 Au revoir !")
                break
            else:
                print("\n❌ Choix invalide. Veuillez entrer un nombre entre 1 et 5.")
                input("\nAppuyez sur Entrée pour continuer...")
