from __future__ import annotations
from typing import Optional
from .models import Zone, ImageCapture, AnalysisVerdict
from .camera import CameraRGB
from .ai_api import AIClient
from .server import CentralServer


class BaseDrone:
    def __init__(self, drone_id: str) -> None:
        self.drone_id = drone_id


class DetectionDrone(BaseDrone):
    """
    Drone 1 : capture des images et envoi à l'API IA. Stocke les résultats de stress dans le serveur.
    """

    def __init__(self, drone_id: str, server: CentralServer) -> None:
        super().__init__(drone_id)
        self.server = server
        self.camera = CameraRGB()
        self.ai = AIClient()

    def process_zone(self, zone: Zone) -> None:
        print(f"[{self.drone_id}] → Zone '{zone.name}' : survol et capture")
        image: ImageCapture = self.camera.capture(zone)
        ai_result = self.ai.analyze_image(
            image_id=image.image_id,
            metadata={
                "zone_name": zone.name,
                "lat": image.lat,
                "lon": image.lon,
                "homogeneity": zone.homogeneity,
                "area_hectares": zone.area_hectares,
                "crop_type": zone.crop_type,
            },
        )
        stress_detected: bool = bool(ai_result.get("stress_detected", False))
        stress_level: float = float(ai_result.get("stress_level", 0.0))
        reason: str = str(ai_result.get("reason", ""))
        verdict = AnalysisVerdict(stress_detected=stress_detected, stress_level=stress_level, reason=reason, crop_type=zone.crop_type)

        print(f"[{self.drone_id}] IA: stress={verdict.stress_detected} niveau={verdict.stress_level:.2f} ({verdict.reason})")

        if verdict.stress_detected:
            self.server.record_stress_point(zone=zone, image=image, verdict=verdict)
            print(f"[{self.drone_id}] → Serveur: point stress enregistré (zone={zone.name})")
        else:
            print(f"[{self.drone_id}] Aucun stress détecté pour '{zone.name}'.")

    def execute_mission(self, mission) -> None:
        for zone in mission.zones:
            self.process_zone(zone)


class MistingDrone(BaseDrone):
    """Drone 2 : lit la file des tâches et brumise avec intensité adaptée."""

    def __init__(self, drone_id: str, server: CentralServer) -> None:
        super().__init__(drone_id)
        self.server = server

    def execute_all_tasks(self) -> None:
        task: Optional[dict] = self.server.pop_next_misting_task()
        if task is None:
            print(f"[{self.drone_id}] Aucune tâche disponible.")
            return

        while task is not None:
            zone = task.get("zone_name")
            lat = float(task.get("lat"))
            lon = float(task.get("lon"))
            volume = float(task.get("volume_l"))
            stress_level = float(task.get("stress_level", 0.0))

            intensity = self._map_stress_to_intensity(stress_level)
            print(
                f"[{self.drone_id}] Brumisation: zone='{zone}' @ ({lat:.5f},{lon:.5f}) volume={volume:.2f} L intensity={intensity}"
            )
            print(f"[{self.drone_id}] Brumisation terminée pour '{zone}'.")
            task = self.server.pop_next_misting_task()

    @staticmethod
    def _map_stress_to_intensity(s: float) -> str:
        if s < 0.33:
            return "low"
        if s < 0.66:
            return "medium"
        return "high"

