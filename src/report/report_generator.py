import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image

class ReportGenerator:
    """
    Genera un reporte visual (imagen con zonas resaltadas)
    y un reporte textual con los resultados de los analizadores.
    """

    def __init__(self):
        pass

    def overlay_masks(self, orig_bgr, masks, alpha=0.4):
        """
        Superpone las máscaras de las zonas sospechosas sobre la imagen original.
        """
        overlay = orig_bgr.copy()
        for mask, color in masks:
            # Ajustar tamaño si la máscara no coincide
            if mask.shape[:2] != orig_bgr.shape[:2]:
                mask = cv2.resize(mask, (orig_bgr.shape[1], orig_bgr.shape[0]))
            colored = np.zeros_like(orig_bgr)
            colored[:, :] = color
            mask3 = (mask > 0).astype('uint8')[:, :, None]
            overlay = np.where(mask3, cv2.addWeighted(overlay, 1 - alpha, colored, alpha, 0), overlay)
        return overlay

    def to_base64(self, image_bgr):
        """
        Convierte una imagen BGR en cadena base64 para mostrar en HTML.
        """
        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        buf = BytesIO()
        pil.save(buf, format='PNG')
        return base64.b64encode(buf.getvalue()).decode('ascii')

    def generate(self, orig_bgr, results):
        """
        Combina resultados de análisis en un reporte visual y textual.
        """
        masks = []
        if "suspicious_mask" in results:
            masks.append((results["suspicious_mask"], (0, 0, 255)))  # rojo
        if "ela_mask" in results:
            masks.append((results["ela_mask"], (0, 255, 255)))  # amarillo

        overlay = self.overlay_masks(orig_bgr, masks)
        img_b64 = self.to_base64(overlay)

        text = {
            "cloning_count": results.get("cloning_count", 0),
            "cloning_confidence": results.get("cloning_confidence", 0.0),
            "ela_confidence": results.get("ela_confidence", 0.0),
            "metadata": results.get("metadata", {})
        }

        return {"image_base64": img_b64, "text_report": text}
