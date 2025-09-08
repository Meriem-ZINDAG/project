from __future__ import annotations
import random
from typing import Dict, Any


class AIClient:
    """
    Stub API IA: simule l'analyse d'une image et renvoie un score de stress [0,1].
    Dans un cas réel, ce client appelerait un endpoint HTTP/GRPC en envoyant l'image.
    """

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        self.base_url = base_url
        self.api_key = api_key

    def analyze_image(self, image_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        # Simulation: score dépend légèrement de l'hétérogénéité et de la surface
        hetero = 1.0 if metadata.get("homogeneity") == "heterogeneous" else 0.0
        area = float(metadata.get("area_hectares", 1.0))
        base = 0.25 + 0.15 * hetero + min(0.15, 0.03 * max(0.0, area - 1.0))
        score = max(0.0, min(1.0, random.gauss(mu=base, sigma=0.15)))
        # Classification binaire pour simplicité
        return {"stress_detected": score > 0.5, "stress_level": score, "reason": f"AI score {score:.2f}"}

