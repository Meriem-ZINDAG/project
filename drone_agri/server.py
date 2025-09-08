from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, List
from .models import Zone, ImageCapture, AnalysisVerdict, serialize_stress_point


class CentralServer:
    """
    Sert de mémoire partagée entre drones.
    - Persiste les points GPS stressés avec niveau de stress dans un fichier JSON.
    - Expose une file de tâches de brumisation dérivée de ces points.
    """

    def __init__(self, storage_path: Path | str) -> None:
        self.storage_path = Path(storage_path)
        self._data: Dict[str, Any] = {"stress_points": [], "misting_queue": []}
        self._load()

    # Persistence
    def _load(self) -> None:
        if self.storage_path.exists():
            try:
                self._data = json.loads(self.storage_path.read_text(encoding="utf-8"))
            except Exception:
                self._data = {"stress_points": [], "misting_queue": []}

    def _save(self) -> None:
        self.storage_path.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")

    # API utilisées par les drones
    def record_stress_point(self, zone: Zone, image: ImageCapture, verdict: AnalysisVerdict) -> None:
        point = serialize_stress_point(
            {
                "zone_name": zone.name,
                "lat": image.lat,
                "lon": image.lon,
                "stress_level": verdict.stress_level,
                "image_id": image.image_id,
                "reason": verdict.reason,
            }
        )
        self._data.setdefault("stress_points", []).append(point)
        # Construire une tâche de brumisation simple: volume proportionnel au stress et à la surface
        volume_l = max(1.0, min(6.0, 1.0 + 5.0 * verdict.stress_level)) * max(0.2, zone.area_hectares / 2.0)
        self._data.setdefault("misting_queue", []).append(
            {
                "zone_name": zone.name,
                "lat": image.lat,
                "lon": image.lon,
                "volume_l": round(volume_l, 2),
                "stress_level": verdict.stress_level,
            }
        )
        self._save()

    def list_stress_points(self) -> List[Dict[str, Any]]:
        return list(self._data.get("stress_points", []))

    def pop_next_misting_task(self) -> Dict[str, Any] | None:
        queue: List[Dict[str, Any]] = self._data.get("misting_queue", [])
        if not queue:
            return None
        # Prioriser par niveau de stress décroissant
        queue.sort(key=lambda x: x.get("stress_level", 0.0), reverse=True)
        task = queue.pop(0)
        self._save()
        return task

