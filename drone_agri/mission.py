from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
from .models import GPSCoord, Zone


@dataclass(frozen=True)
class Mission:
    zones: List[Zone]

    @staticmethod
    def from_json(payload: Dict[str, Any]) -> "Mission":
        zones_payload: List[Dict[str, Any]] = payload.get("zones", [])
        zones: List[Zone] = []
        for z in zones_payload:
            center = GPSCoord(lat=float(z["center"]["lat"]), lon=float(z["center"]["lon"]))
            zones.append(
                Zone(
                    name=str(z["name"]),
                    center=center,
                    area_hectares=float(z["area_hectares"]),
                    homogeneity=str(z["homogeneity"]),
                    crop_type=str(z["crop_type"]) if z.get("crop_type") else None,
                )
            )
        return Mission(zones=zones)

