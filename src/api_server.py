"""
Module API Flask pour piloter l'optimisation VRP.
Permet d'automatiser la résolution via des requêtes HTTP.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from datetime import datetime

# Import des modules VRP
from data_handler import DataHandler, get_default_clients_data
from optimizer import VRPOptimizer
from visualizer import VRPVisualizer
from analyzer import VRPAnalyzer

# Initialisation de l'application Flask
app = Flask(__name__)
CORS(app)  # Activer CORS pour les requêtes cross-origin

# Dossier de sortie pour les résultats
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.route('/', methods=['GET'])
def home():
    """Point d'entrée de l'API."""
    return jsonify({
        'message': 'API d\'optimisation VRP (Vehicle Routing Problem)',
        'version': '1.0.0',
        'endpoints': {
            'POST /optimize': 'Résoudre un problème VRP',
            'GET /results/<result_id>': 'Récupérer les résultats d\'une optimisation',
            'GET /visualizations/<result_id>/<type>': 'Récupérer une visualisation',
            'GET /health': 'Vérifier l\'état de l\'API'
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """Vérification de l'état de l'API."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/optimize', methods=['POST'])
def optimize():
    """
    Résout un problème VRP.
    
    Body JSON:
    {
        "clients_data": {...},  # Optionnel, utilise les données par défaut si absent
        "config": {
            "num_vehicles": 3,
            "vehicle_capacity": 50,
            "weight_distance": 1.0,
            "weight_priority": 0.5,
            "weight_time": 0.3,
            "time_limit": 30
        }
    }
    
    Returns:
        JSON avec la solution et l'ID des résultats
    """
    try:
        # Récupérer les données de la requête
        data = request.get_json()
        
        # Utiliser les données par défaut si non fournies
        clients_data = data.get('clients_data', get_default_clients_data())
        
        # Configuration par défaut
        default_config = {
            'num_vehicles': 3,
            'vehicle_capacity': 50,
            'weight_distance': 1.0,
            'weight_priority': 0.5,
            'weight_time': 0.3,
            'time_limit': 30,
            'verbose': False
        }
        
        # Fusionner avec la configuration fournie
        config = {**default_config, **data.get('config', {})}
        
        # Charger les données
        data_handler = DataHandler()
        data_handler.load_clients_data(clients_data)
        data_handler.calculate_distance_matrix()
        
        # Optimiser
        optimizer = VRPOptimizer(data_handler, config)
        solution = optimizer.solve()
        
        if not solution:
            return jsonify({
                'success': False,
                'error': 'Aucune solution trouvée'
            }), 400
        
        # Générer un ID unique pour les résultats
        result_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Créer les visualisations
        visualizer = VRPVisualizer(data_handler)
        result_dir = os.path.join(OUTPUT_DIR, result_id)
        visualizer.create_all_visualizations(solution, output_dir=result_dir)
        
        # Analyser les résultats
        analyzer = VRPAnalyzer(data_handler, solution, config)
        metrics = analyzer.calculate_metrics()
        recommendations = analyzer.generate_recommendations()
        comparison = analyzer.compare_with_baseline()
        
        # Sauvegarder les résultats complets
        full_results = {
            'result_id': result_id,
            'timestamp': datetime.now().isoformat(),
            'config': config,
            'solution': solution,
            'metrics': metrics,
            'recommendations': recommendations,
            'comparison': comparison
        }
        
        results_file = os.path.join(result_dir, 'results.json')
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(full_results, f, indent=2, ensure_ascii=False)
        
        # Retourner une réponse simplifiée
        return jsonify({
            'success': True,
            'result_id': result_id,
            'summary': {
                'total_distance': solution['total_distance'],
                'total_load': solution['total_load'],
                'num_vehicles_used': len(solution['vehicle_stats']),
                'clients_served': metrics['clients_served'],
                'service_rate': metrics['service_rate']
            },
            'metrics': metrics,
            'recommendations': recommendations,
            'comparison': comparison,
            'visualizations': {
                'routes': f'/visualizations/{result_id}/routes',
                'comparison': f'/visualizations/{result_id}/comparison',
                'timeline': f'/visualizations/{result_id}/timeline'
            },
            'results_url': f'/results/{result_id}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/results/<result_id>', methods=['GET'])
def get_results(result_id):
    """
    Récupère les résultats complets d'une optimisation.
    
    Args:
        result_id: ID des résultats
    
    Returns:
        JSON avec tous les résultats
    """
    try:
        results_file = os.path.join(OUTPUT_DIR, result_id, 'results.json')
        
        if not os.path.exists(results_file):
            return jsonify({
                'success': False,
                'error': 'Résultats non trouvés'
            }), 404
        
        with open(results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/visualizations/<result_id>/<viz_type>', methods=['GET'])
def get_visualization(result_id, viz_type):
    """
    Récupère une visualisation spécifique.
    
    Args:
        result_id: ID des résultats
        viz_type: Type de visualisation (routes, comparison, timeline)
    
    Returns:
        Image PNG de la visualisation
    """
    try:
        viz_files = {
            'routes': 'vrp_routes.png',
            'comparison': 'vrp_comparison.png',
            'timeline': 'vrp_timeline.png'
        }
        
        if viz_type not in viz_files:
            return jsonify({
                'success': False,
                'error': 'Type de visualisation invalide'
            }), 400
        
        viz_file = os.path.join(OUTPUT_DIR, result_id, viz_files[viz_type])
        
        if not os.path.exists(viz_file):
            return jsonify({
                'success': False,
                'error': 'Visualisation non trouvée'
            }), 404
        
        return send_file(viz_file, mimetype='image/png')
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/list-results', methods=['GET'])
def list_results():
    """
    Liste tous les résultats disponibles.
    
    Returns:
        JSON avec la liste des résultats
    """
    try:
        results = []
        
        if os.path.exists(OUTPUT_DIR):
            for item in os.listdir(OUTPUT_DIR):
                item_path = os.path.join(OUTPUT_DIR, item)
                if os.path.isdir(item_path):
                    results_file = os.path.join(item_path, 'results.json')
                    if os.path.exists(results_file):
                        with open(results_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            results.append({
                                'result_id': item,
                                'timestamp': data.get('timestamp'),
                                'total_distance': data['solution']['total_distance'],
                                'num_vehicles_used': len(data['solution']['vehicle_stats'])
                            })
        
        # Trier par timestamp décroissant
        results.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/default-config', methods=['GET'])
def get_default_config():
    """
    Retourne la configuration par défaut.
    
    Returns:
        JSON avec la configuration par défaut
    """
    return jsonify({
        'success': True,
        'config': {
            'num_vehicles': 3,
            'vehicle_capacity': 50,
            'weight_distance': 1.0,
            'weight_priority': 0.5,
            'weight_time': 0.3,
            'time_limit': 30
        },
        'clients_data': get_default_clients_data()
    })


def run_server(host='0.0.0.0', port=5000, debug=True):
    """
    Lance le serveur Flask.
    
    Args:
        host: Adresse d'écoute
        port: Port d'écoute
        debug: Mode debug
    """
    print("=" * 80)
    print("🚀 DÉMARRAGE DU SERVEUR API VRP")
    print("=" * 80)
    print(f"\n📍 URL: http://{host}:{port}")
    print(f"📊 Dossier de sortie: {OUTPUT_DIR}")
    print("\n💡 Endpoints disponibles:")
    print(f"  - GET  http://{host}:{port}/")
    print(f"  - POST http://{host}:{port}/optimize")
    print(f"  - GET  http://{host}:{port}/results/<result_id>")
    print(f"  - GET  http://{host}:{port}/visualizations/<result_id>/<type>")
    print(f"  - GET  http://{host}:{port}/list-results")
    print(f"  - GET  http://{host}:{port}/default-config")
    print(f"  - GET  http://{host}:{port}/health")
    print("\n" + "=" * 80 + "\n")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_server()
