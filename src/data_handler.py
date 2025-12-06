"""
Module de gestion des données pour le problème VRP (Vehicle Routing Problem).
Ce module contient les fonctions pour charger, valider et préparer les données des clients.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class DataHandler:
    """Classe pour gérer les données des clients et du dépôt."""
    
    def __init__(self):
        """Initialise le gestionnaire de données."""
        self.clients_df = None
        self.distance_matrix = None
        self.num_locations = 0
        
    def load_clients_data(self, clients_data: Dict) -> pd.DataFrame:
        """
        Charge les données des clients à partir d'un dictionnaire.
        
        Args:
            clients_data: Dictionnaire contenant les informations des clients
                - id: identifiants des clients
                - nom: noms des clients
                - x, y: coordonnées géographiques
                - demande: quantité demandée par chaque client
                - temps_service: temps de service en minutes
                - fenetre_debut, fenetre_fin: fenêtres horaires en minutes
                - priorite: niveau de priorité (1=haute, 2=moyenne, 3=basse)
        
        Returns:
            DataFrame pandas contenant les données des clients
        """
        self.clients_df = pd.DataFrame(clients_data)
        self.num_locations = len(self.clients_df)
        
        # Validation des données
        self._validate_data()
        
        print(f"✓ Données chargées : {self.num_locations} lieux (1 dépôt + {self.num_locations - 1} clients)")
        print(f"  - Demande totale : {self.clients_df['demande'].sum()} unités")
        print(f"  - Temps de service total : {self.clients_df['temps_service'].sum()} minutes")
        
        return self.clients_df
    
    def _validate_data(self):
        """Valide la cohérence des données chargées."""
        required_columns = ['id', 'nom', 'x', 'y', 'demande', 'temps_service', 
                           'fenetre_debut', 'fenetre_fin', 'priorite']
        
        for col in required_columns:
            if col not in self.clients_df.columns:
                raise ValueError(f"Colonne manquante : {col}")
        
        # Vérification que le dépôt (id=0) a une demande nulle
        if self.clients_df.loc[0, 'demande'] != 0:
            raise ValueError("Le dépôt (id=0) doit avoir une demande nulle")
        
        # Vérification que les fenêtres horaires sont cohérentes
        if (self.clients_df['fenetre_debut'] > self.clients_df['fenetre_fin']).any():
            raise ValueError("Certaines fenêtres horaires sont incohérentes (début > fin)")
    
    def calculate_distance_matrix(self) -> np.ndarray:
        """
        Calcule la matrice des distances euclidiennes entre tous les lieux.
        
        Returns:
            Matrice numpy de dimensions (n x n) des distances
        """
        n = self.num_locations
        self.distance_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Distance euclidienne
                    dx = self.clients_df.loc[i, 'x'] - self.clients_df.loc[j, 'x']
                    dy = self.clients_df.loc[i, 'y'] - self.clients_df.loc[j, 'y']
                    self.distance_matrix[i][j] = np.sqrt(dx**2 + dy**2)
        
        print(f"✓ Matrice de distances calculée ({n}x{n})")
        print(f"  - Distance moyenne : {self.distance_matrix[self.distance_matrix > 0].mean():.2f} unités")
        print(f"  - Distance max : {self.distance_matrix.max():.2f} unités")
        
        return self.distance_matrix
    
    def get_location_coordinates(self) -> List[Tuple[float, float]]:
        """
        Retourne la liste des coordonnées (x, y) de tous les lieux.
        
        Returns:
            Liste de tuples (x, y)
        """
        return list(zip(self.clients_df['x'], self.clients_df['y']))
    
    def get_demands(self) -> List[int]:
        """
        Retourne la liste des demandes de tous les lieux.
        
        Returns:
            Liste des demandes
        """
        return self.clients_df['demande'].tolist()
    
    def get_time_windows(self) -> List[Tuple[int, int]]:
        """
        Retourne la liste des fenêtres horaires de tous les lieux.
        
        Returns:
            Liste de tuples (début, fin)
        """
        return list(zip(self.clients_df['fenetre_debut'], 
                       self.clients_df['fenetre_fin']))
    
    def get_service_times(self) -> List[int]:
        """
        Retourne la liste des temps de service de tous les lieux.
        
        Returns:
            Liste des temps de service
        """
        return self.clients_df['temps_service'].tolist()
    
    def get_priorities(self) -> List[int]:
        """
        Retourne la liste des priorités de tous les lieux.
        
        Returns:
            Liste des priorités
        """
        return self.clients_df['priorite'].tolist()
    
    def get_client_info(self, client_id: int) -> Dict:
        """
        Retourne les informations détaillées d'un client spécifique.
        
        Args:
            client_id: ID du client
        
        Returns:
            Dictionnaire contenant les informations du client
        """
        if client_id >= self.num_locations:
            raise ValueError(f"ID client invalide : {client_id}")
        
        row = self.clients_df.loc[client_id]
        return {
            'id': int(row['id']),
            'nom': row['nom'],
            'coordonnees': (float(row['x']), float(row['y'])),
            'demande': int(row['demande']),
            'temps_service': int(row['temps_service']),
            'fenetre_horaire': (int(row['fenetre_debut']), int(row['fenetre_fin'])),
            'priorite': int(row['priorite'])
        }
    
    def export_to_csv(self, filepath: str):
        """
        Exporte les données des clients dans un fichier CSV.
        
        Args:
            filepath: Chemin du fichier de sortie
        """
        self.clients_df.to_csv(filepath, index=False)
        print(f"✓ Données exportées vers : {filepath}")


def get_default_clients_data() -> Dict:
    """
    Retourne les données par défaut des clients.
    
    Returns:
        Dictionnaire contenant les données des clients
    """
    return {
        'id': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        'nom': ['Dépôt', 'Client_01', 'Client_02', 'Client_03', 'Client_04', 'Client_05', 
                'Client_06', 'Client_07', 'Client_08', 'Client_09', 'Client_10', 'Client_11',
                'Client_12', 'Client_13', 'Client_14', 'Client_15', 'Client_16', 'Client_17',
                'Client_18', 'Client_19', 'Client_20'],
        'x': [25.0, 40.15, 32.76, 19.51, 12.66, 29.48, 36.55, 21.89, 17.26, 13.38, 
              33.17, 25.33, 30.08, 16.87, 22.66, 28.95, 11.02, 43.24, 39.77, 18.65, 27.14],
        'y': [25.0, 16.24, 38.14, 13.12, 21.09, 10.02, 44.71, 31.77, 42.92, 34.61,
              19.74, 10.15, 39.17, 18.33, 45.05, 33.67, 25.88, 23.45, 32.54, 27.46, 41.55],
        'demande': [0, 4, 7, 6, 8, 5, 10, 2, 3, 7, 5, 6, 4, 8, 5, 2, 10, 9, 6, 3, 8],
        'temps_service': [0, 11, 12, 10, 8, 9, 13, 7, 6, 9, 11, 10, 7, 12, 8, 5, 10, 14, 9, 7, 12],
        'fenetre_debut': [0, 480, 0, 0, 780, 0, 0, 480, 0, 780, 0, 480, 0, 780, 0, 0, 480, 0, 0, 780, 0],
        'fenetre_fin': [1440, 720, 1440, 1440, 1020, 1440, 1440, 720, 1440, 1020, 1440, 720, 1440, 1020, 1440, 1440, 720, 1440, 1440, 1020, 1440],
        'priorite': [0, 1, 1, 1, 1, 2, 1, 1, 1, 3, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2]
    }
