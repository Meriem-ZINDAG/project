import argparse
import json
import random
from pathlib import Path

from drone_agri.mission import Mission
from drone_agri.server import CentralServer
from drone_agri.drones import DetectionDrone, MistingDrone


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simulation: Drone 1 (détection) + Drone 2 (brumisation)")
    parser.add_argument("--mission", required=True, help="Chemin du fichier JSON de mission")
    parser.add_argument("--seed", type=int, default=None, help="Graine aléatoire pour la reproductibilité")
    parser.add_argument("--storage", type=Path, default=Path("server_data.json"), help="Fichier JSON de stockage serveur")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.seed is not None:
        random.seed(args.seed)

    with open(args.mission, "r", encoding="utf-8") as f:
        mission_payload = json.load(f)

    mission = Mission.from_json(mission_payload)
    server = CentralServer(storage_path=args.storage)

    detection_drone = DetectionDrone(drone_id="DRONE-DETECT-1", server=server)
    misting_drone = MistingDrone(drone_id="DRONE-MIST-1", server=server)

    print("=== DÉMARRAGE MISSION (Détection) ===")
    detection_drone.execute_mission(mission)

    print("\n=== ÉTAT SERVEUR: Points stress enregistrés ===")
    for p in server.list_stress_points():
        print(f"- zone={p['zone_name']} lat={p['lat']:.5f} lon={p['lon']:.5f} s={p['stress_level']:.2f} image_id={p['image_id']}")

    print("\n=== EXÉCUTION BRUMISATION (Drone 2) ===")
    misting_drone.execute_all_tasks()

    print("\n=== FIN ===")


if __name__ == "__main__":
    main()

