"""
Script de test pour vérifier que le projet VRP est correctement installé et fonctionne.
Exécutez ce script après avoir installé les dépendances pour vérifier que tout fonctionne.
"""

import sys
import os

def test_imports():
    """Teste l'importation des modules nécessaires."""
    print("\n1️⃣  Test des imports...")
    
    try:
        import ortools
        print("   ✓ ortools")
    except ImportError as e:
        print(f"   ❌ ortools: {e}")
        return False
    
    try:
        import flask
        print("   ✓ flask")
    except ImportError as e:
        print(f"   ❌ flask: {e}")
        return False
    
    try:
        import matplotlib
        print("   ✓ matplotlib")
    except ImportError as e:
        print(f"   ❌ matplotlib: {e}")
        return False
    
    try:
        import pandas
        print("   ✓ pandas")
    except ImportError as e:
        print(f"   ❌ pandas: {e}")
        return False
    
    try:
        import numpy
        print("   ✓ numpy")
    except ImportError as e:
        print(f"   ❌ numpy: {e}")
        return False
    
    return True


def test_modules():
    """Teste l'importation des modules VRP."""
    print("\n2️⃣  Test des modules VRP...")
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from src.data_handler import DataHandler, get_default_clients_data
        print("   ✓ data_handler")
    except Exception as e:
        print(f"   ❌ data_handler: {e}")
        return False
    
    try:
        from src.optimizer import VRPOptimizer
        print("   ✓ optimizer")
    except Exception as e:
        print(f"   ❌ optimizer: {e}")
        return False
    
    try:
        from src.visualizer import VRPVisualizer
        print("   ✓ visualizer")
    except Exception as e:
        print(f"   ❌ visualizer: {e}")
        return False
    
    try:
        from src.analyzer import VRPAnalyzer
        print("   ✓ analyzer")
    except Exception as e:
        print(f"   ❌ analyzer: {e}")
        return False
    
    try:
        from src.api_server import app
        print("   ✓ api_server")
    except Exception as e:
        print(f"   ❌ api_server: {e}")
        return False
    
    return True


def test_optimization():
    """Teste une optimisation simple."""
    print("\n3️⃣  Test d'optimisation...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from src.data_handler import DataHandler, get_default_clients_data
        from src.optimizer import VRPOptimizer
        
        # Configuration minimale
        config = {
            'num_vehicles': 3,
            'vehicle_capacity': 50,
            'weight_distance': 1.0,
            'weight_priority': 0.5,
            'weight_time': 0.3,
            'time_limit': 10,  # Court pour le test
            'verbose': False
        }
        
        # Charger les données
        data_handler = DataHandler()
        clients_data = get_default_clients_data()
        data_handler.load_clients_data(clients_data)
        data_handler.calculate_distance_matrix()
        
        # Optimiser
        optimizer = VRPOptimizer(data_handler, config)
        solution = optimizer.solve()
        
        if solution and len(solution['vehicle_stats']) > 0:
            print(f"   ✓ Solution trouvée: {solution['total_distance']:.2f} unités")
            print(f"   ✓ {len(solution['vehicle_stats'])} véhicules utilisés")
            print(f"   ✓ {solution['total_load']} unités de charge totale")
            return True
        else:
            print("   ❌ Aucune solution valide trouvée")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur d'optimisation: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_output_directory():
    """Teste la création du dossier de sortie."""
    print("\n4️⃣  Test du dossier de sortie...")
    
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    
    if os.path.exists(output_dir):
        print(f"   ✓ Dossier output existe: {output_dir}")
        return True
    else:
        print(f"   ⚠️  Dossier output n'existe pas, création...")
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"   ✓ Dossier créé: {output_dir}")
            return True
        except Exception as e:
            print(f"   ❌ Erreur de création: {e}")
            return False


def main():
    """Fonction principale de test."""
    print("=" * 80)
    print("🧪 TEST D'INSTALLATION DU PROJET VRP")
    print("=" * 80)
    
    results = {
        'imports': test_imports(),
        'modules': test_modules(),
        'output': test_output_directory(),
        'optimization': test_optimization()
    }
    
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 80)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ TOUS LES TESTS ONT RÉUSSI!")
        print("\nVous pouvez maintenant utiliser le projet :")
        print("  • Mode interactif : python main.py")
        print("  • Mode automatique : python main.py auto")
        print("  • API Flask       : python main.py api")
        print("  • Aide            : python main.py help")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("\nVérifiez les erreurs ci-dessus et :")
        print("  1. Installez les dépendances : pip install -r requirements.txt")
        print("  2. Vérifiez votre version de Python (>= 3.8)")
        print("  3. Consultez la documentation dans docs/")
    print("=" * 80)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
