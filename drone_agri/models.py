from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass(frozen=True)
class GPSCoord:
    lat: float
    lon: float


@dataclass(frozen=True)
class Zone:
    name: str
    center: GPSCoord
    area_hectares: float
    homogeneity: str  # "homogeneous" | "heterogeneous"
    crop_type: Optional[str] = None


@dataclass(frozen=True)
class ImageCapture:
    image_id: str
    zone_name: str
    lat: float
    lon: float


@dataclass(frozen=True)
class AnalysisVerdict:
    stress_detected: bool
    stress_level: float  # [0,1]
    reason: str
    crop_type: Optional[str] = None


def serialize_stress_point(point: Dict[str, Any]) -> Dict[str, Any]:
    # ensure values are JSON-serializable (floats rounded)
    return {
        "zone_name": str(point["zone_name"]),
        "lat": float(point["lat"]),
        "lon": float(point["lon"]),
        "stress_level": float(point["stress_level"]),
        "image_id": str(point.get("image_id", "")),
        "reason": str(point.get("reason", "")),
    }

