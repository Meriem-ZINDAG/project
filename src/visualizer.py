"""
Module de visualisation pour le problème VRP.
Crée des graphiques 2D des tournées optimisées.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List
import os


class VRPVisualizer:
    """Classe pour visualiser les tournées de véhicules."""
    
    def __init__(self, data_handler):
        """
        Initialise le visualiseur.
        
        Args:
            data_handler: Instance de DataHandler contenant les données
        """
        self.data_handler = data_handler
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
                       '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788']
    
    def plot_routes(self, solution: Dict, save_path: str = None, show: bool = True):
        """
        Visualise les tournées sur un graphique 2D.
        
        Args:
            solution: Dictionnaire contenant la solution
            save_path: Chemin pour sauvegarder l'image (optionnel)
            show: Si True, affiche le graphique
        """
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Récupérer les coordonnées
        coords = self.data_handler.get_location_coordinates()
        x_coords = [c[0] for c in coords]
        y_coords = [c[1] for c in coords]
        
        # Tracer le dépôt
        depot_x, depot_y = coords[0]
        ax.scatter(depot_x, depot_y, c='red', s=400, marker='s', 
                  edgecolors='black', linewidths=2, zorder=5, label='Dépôt')
        ax.text(depot_x, depot_y, 'Dépôt', fontsize=10, ha='center', 
               va='center', weight='bold', color='white')
        
        # Tracer les clients
        for i in range(1, len(coords)):
            x, y = coords[i]
            priority = self.data_handler.clients_df.loc[i, 'priorite']
            
            # Couleur selon la priorité
            if priority == 1:
                color = 'gold'
                marker = '*'
                size = 300
                edge = 'darkred'
            elif priority == 2:
                color = 'orange'
                marker = 'o'
                size = 200
                edge = 'darkorange'
            else:
                color = 'lightblue'
                marker = 'o'
                size = 150
                edge = 'blue'
            
            ax.scatter(x, y, c=color, s=size, marker=marker, 
                      edgecolors=edge, linewidths=1.5, zorder=4)
            ax.text(x, y + 1.5, f'C{i}', fontsize=8, ha='center', weight='bold')
        
        # Tracer les routes pour chaque véhicule
        for idx, stats in enumerate(solution['vehicle_stats']):
            route = stats['route']
            color = self.colors[idx % len(self.colors)]
            
            # Tracer les segments de la route
            for i in range(len(route) - 1):
                start_node = route[i]
                end_node = route[i + 1]
                
                x_start, y_start = coords[start_node]
                x_end, y_end = coords[end_node]
                
                # Ligne avec flèche
                ax.annotate('', xy=(x_end, y_end), xytext=(x_start, y_start),
                           arrowprops=dict(arrowstyle='->', lw=2, color=color, alpha=0.7))
                
                # Ajouter le numéro de séquence
                mid_x = (x_start + x_end) / 2
                mid_y = (y_start + y_end) / 2
                ax.text(mid_x, mid_y, str(i + 1), fontsize=7, 
                       bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.5))
        
        # Légende des véhicules
        legend_elements = []
        for idx, stats in enumerate(solution['vehicle_stats']):
            color = self.colors[idx % len(self.colors)]
            label = f"Véhicule {stats['vehicle_id'] + 1} ({stats['distance']:.1f} unités)"
            legend_elements.append(plt.Line2D([0], [0], color=color, lw=3, label=label))
        
        # Légende des priorités
        legend_elements.extend([
            plt.Line2D([0], [0], marker='*', color='w', markerfacecolor='gold', 
                      markersize=12, label='Priorité Haute', markeredgecolor='darkred'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', 
                      markersize=10, label='Priorité Moyenne', markeredgecolor='darkorange'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', 
                      markersize=8, label='Priorité Basse', markeredgecolor='blue')
        ])
        
        ax.legend(handles=legend_elements, loc='upper left', fontsize=9, 
                 framealpha=0.9, shadow=True)
        
        # Configuration du graphique
        ax.set_xlabel('Coordonnée X', fontsize=12, weight='bold')
        ax.set_ylabel('Coordonnée Y', fontsize=12, weight='bold')
        ax.set_title('Optimisation des Tournées de Livraison (VRP)\n' + 
                    f'Distance totale: {solution["total_distance"]:.2f} unités',
                    fontsize=14, weight='bold', pad=20)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_aspect('equal')
        
        # Ajuster les limites
        margin = 5
        ax.set_xlim(min(x_coords) - margin, max(x_coords) + margin)
        ax.set_ylim(min(y_coords) - margin, max(y_coords) + margin)
        
        plt.tight_layout()
        
        # Sauvegarder si demandé
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Visualisation sauvegardée : {save_path}")
        
        # Afficher si demandé
        if show:
            plt.show()
        else:
            plt.close()
    
    def plot_distance_comparison(self, solution: Dict, save_path: str = None, show: bool = True):
        """
        Crée un graphique en barres comparant les distances par véhicule.
        
        Args:
            solution: Dictionnaire contenant la solution
            save_path: Chemin pour sauvegarder l'image (optionnel)
            show: Si True, affiche le graphique
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Graphique 1: Distances par véhicule
        vehicles = [f"V{stats['vehicle_id'] + 1}" for stats in solution['vehicle_stats']]
        distances = [stats['distance'] for stats in solution['vehicle_stats']]
        colors_bar = [self.colors[i % len(self.colors)] for i in range(len(vehicles))]
        
        bars1 = ax1.bar(vehicles, distances, color=colors_bar, edgecolor='black', linewidth=1.5)
        ax1.set_xlabel('Véhicule', fontsize=12, weight='bold')
        ax1.set_ylabel('Distance (unités)', fontsize=12, weight='bold')
        ax1.set_title('Distance parcourue par véhicule', fontsize=13, weight='bold')
        ax1.grid(True, alpha=0.3, axis='y', linestyle='--')
        
        # Ajouter les valeurs sur les barres
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom', fontsize=10, weight='bold')
        
        # Graphique 2: Charge par véhicule
        loads = [stats['load'] for stats in solution['vehicle_stats']]
        capacity_used = [stats['capacity_used'] for stats in solution['vehicle_stats']]
        
        bars2 = ax2.bar(vehicles, capacity_used, color=colors_bar, 
                       edgecolor='black', linewidth=1.5)
        ax2.set_xlabel('Véhicule', fontsize=12, weight='bold')
        ax2.set_ylabel('Taux d\'utilisation (%)', fontsize=12, weight='bold')
        ax2.set_title('Taux d\'utilisation de la capacité', fontsize=13, weight='bold')
        ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
        ax2.axhline(y=100, color='red', linestyle='--', linewidth=2, label='Capacité max')
        ax2.legend()
        
        # Ajouter les valeurs sur les barres
        for i, bar in enumerate(bars2):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{height:.1f}%\n({loads[i]} u.)',
                    ha='center', va='bottom', fontsize=9, weight='bold')
        
        plt.tight_layout()
        
        # Sauvegarder si demandé
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Graphique de comparaison sauvegardé : {save_path}")
        
        # Afficher si demandé
        if show:
            plt.show()
        else:
            plt.close()
    
    def plot_timeline(self, solution: Dict, save_path: str = None, show: bool = True):
        """
        Crée un diagramme de Gantt montrant la chronologie des tournées.
        
        Args:
            solution: Dictionnaire contenant la solution
            save_path: Chemin pour sauvegarder l'image (optionnel)
            show: Si True, affiche le graphique
        """
        fig, ax = plt.subplots(figsize=(14, 8))
        
        y_ticks = []
        y_labels = []
        
        for idx, stats in enumerate(solution['vehicle_stats']):
            vehicle_id = stats['vehicle_id']
            route_info = stats['route_info']
            color = self.colors[idx % len(self.colors)]
            
            y_pos = vehicle_id
            y_ticks.append(y_pos)
            y_labels.append(f"Véhicule {vehicle_id + 1}")
            
            # Tracer les segments de temps
            for i in range(len(route_info) - 1):
                start_time = route_info[i]['arrival_time']
                end_time = route_info[i + 1]['arrival_time']
                
                # Barre horizontale
                ax.barh(y_pos, end_time - start_time, left=start_time, 
                       height=0.6, color=color, edgecolor='black', linewidth=1, alpha=0.7)
                
                # Ajouter le nom du client
                mid_time = (start_time + end_time) / 2
                client_name = route_info[i]['nom'] if i > 0 else ''
                if client_name and client_name != 'Dépôt':
                    ax.text(mid_time, y_pos, client_name, 
                           ha='center', va='center', fontsize=8, weight='bold')
        
        ax.set_xlabel('Temps (minutes)', fontsize=12, weight='bold')
        ax.set_ylabel('Véhicule', fontsize=12, weight='bold')
        ax.set_title('Chronologie des tournées de livraison', fontsize=14, weight='bold')
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels)
        ax.grid(True, alpha=0.3, axis='x', linestyle='--')
        
        # Convertir l'axe X en format horaire
        x_ticks = ax.get_xticks()
        x_labels = [f"{int(t // 60):02d}h{int(t % 60):02d}" for t in x_ticks]
        ax.set_xticklabels(x_labels, rotation=45)
        
        plt.tight_layout()
        
        # Sauvegarder si demandé
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Chronologie sauvegardée : {save_path}")
        
        # Afficher si demandé
        if show:
            plt.show()
        else:
            plt.close()
    
    def create_all_visualizations(self, solution: Dict, output_dir: str = 'output'):
        """
        Crée toutes les visualisations et les sauvegarde.
        
        Args:
            solution: Dictionnaire contenant la solution
            output_dir: Dossier de sortie
        """
        print("\n📊 Génération des visualisations...")
        
        # Créer le dossier de sortie s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)
        
        # Visualisation des routes
        routes_path = os.path.join(output_dir, 'vrp_routes.png')
        self.plot_routes(solution, save_path=routes_path, show=False)
        
        # Comparaison des distances
        comparison_path = os.path.join(output_dir, 'vrp_comparison.png')
        self.plot_distance_comparison(solution, save_path=comparison_path, show=False)
        
        # Chronologie
        timeline_path = os.path.join(output_dir, 'vrp_timeline.png')
        self.plot_timeline(solution, save_path=timeline_path, show=False)
        
        print(f"✓ Toutes les visualisations ont été générées dans : {output_dir}")
