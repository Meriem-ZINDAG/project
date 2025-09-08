from __future__ import annotations
import uuid
from .models import Zone, ImageCapture


class CameraRGB:
    """Stub caméra: retourne un identifiant d'image et les coordonnées de capture."""

    def capture(self, zone: Zone) -> ImageCapture:
        image_id = str(uuid.uuid4())
        return ImageCapture(
            image_id=image_id,
            zone_name=zone.name,
            lat=zone.center.lat,
            lon=zone.center.lon,
        )

