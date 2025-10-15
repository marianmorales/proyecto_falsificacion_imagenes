from PIL import Image
import numpy as np
import io
import cv2
import os
from .base_analyzer import BaseAnalyzer

class CompressionAnalyzer(BaseAnalyzer):
    """
    Analizador de compresión (Error Level Analysis - ELA):
    Detecta posibles alteraciones comparando la imagen original
    con una versión recomprimida en JPEG.
    Se adapta automáticamente según el formato del archivo.
    """

    def __init__(self, quality=90, scale=10):
        self.quality = quality
        self.scale = scale

    def analyze(self, image, info=None):
        # Determinar el tipo de archivo original (si hay filepath)
        file_format = None
        if info and isinstance(info, dict) and info.get("filepath"):
            _, ext = os.path.splitext(info["filepath"])
            file_format = ext.lower().replace(".", "")

        # Convertir imagen BGR (OpenCV) a RGB (PIL)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb)

        # Recomprensión JPEG en memoria
        buffer = io.BytesIO()
        pil_image.save(buffer, 'JPEG', quality=self.quality)
        buffer.seek(0)
        recompressed = Image.open(buffer)

        # Convertir a arrays NumPy
        arr_orig = np.array(pil_image).astype('int32')
        arr_comp = np.array(recompressed).astype('int32')

        # Asegurar mismo tamaño
        min_h = min(arr_orig.shape[0], arr_comp.shape[0])
        min_w = min(arr_orig.shape[1], arr_comp.shape[1])
        diff = np.abs(arr_orig[:min_h, :min_w] - arr_comp[:min_h, :min_w])

        # Escalar diferencias para visualización
        ela = np.clip(diff * self.scale, 0, 255).astype('uint8')
        ela_bgr = cv2.cvtColor(ela, cv2.COLOR_RGB2BGR)

        # Convertir a escala de grises
        ela_gray = cv2.cvtColor(ela_bgr, cv2.COLOR_BGR2GRAY)

        # Ajustar sensibilidad según formato
        if file_format == "jpg" or file_format == "jpeg":
            threshold = 50   # más alto para no sobrerreaccionar
            factor = 0.2     # reduce la influencia del ELA en JPEGs
        else:
            threshold = 30   # más sensible en PNG o BMP
            factor = 1.0

        # Crear máscara binaria
        _, mask = cv2.threshold(ela_gray, threshold, 255, cv2.THRESH_BINARY)

        # Calcular proporción de píxeles sospechosos
        ratio = mask.sum() / (mask.size * 255)

        # Calcular confianza ajustada por formato
        if ratio < 0.002:
            confidence = 0.0
        elif ratio < 0.01:
            confidence = 0.3 * factor
        elif ratio < 0.05:
            confidence = 0.6 * factor
        else:
            confidence = 1.0 * factor

        result = {
            "ela_image": ela_bgr,
            "ela_mask": mask,
            "ela_confidence": confidence,
        }

        if file_format in ["jpg", "jpeg"]:
            result["note"] = " Imagen JPEG detectada: resultados ELA pueden no ser confiables."
        else:
            result["note"] = "Formato sin pérdida detectado: análisis ELA más confiable."

        return result
