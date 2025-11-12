import cv2
import base64
import numpy as np
import os
from src.analyzers.preprocessing_analyzer import PreprocessingAnalyzer
from src.analyzers.cloning_analyzer import CloningAnalyzer
from src.analyzers.compression_analyzer import CompressionAnalyzer
from src.analyzers.metadata_analyzer import MetadataAnalyzer
from src.report.report_generator import ReportGenerator


class ImageForgeryDetector:
    """
    Clase principal que coordina los análisis de manipulación de imagen.
    """

    def __init__(self):
        self.pre = PreprocessingAnalyzer()
        self.clone = CloningAnalyzer(block_size=32)
        self.comp = CompressionAnalyzer(quality=90)
        self.meta = MetadataAnalyzer()
        self.reporter = ReportGenerator()

    def analyze_from_path(self, filepath):
        """
        Carga una imagen desde el disco y la analiza.
        """
        img = cv2.imread(filepath)
        if img is None:
            raise ValueError(f"No se pudo cargar la imagen desde: {filepath}")
        return self._analyze(img, info={"filepath": filepath})

    def analyze_from_array(self, bgr_image):
        """
        Analiza una imagen recibida como array (por ejemplo, desde Flask).
        """
        return self._analyze(bgr_image, info=None)

    def _analyze(self, img_bgr, info=None):
        """
        Ejecuta la secuencia completa de análisis y genera reporte visual y textual.
        """
        # --- Etapas de análisis individuales ---
        pre = self.pre.analyze(img_bgr)
        clon = self.clone.analyze(img_bgr)
        comp = self.comp.analyze(img_bgr)
        meta = self.meta.analyze(img_bgr, info=info)

        # --- Cálculo de confiabilidad combinada ---
        cloning_conf = clon.get("confidence", 0.0)
        ela_conf = comp.get("confidence", 0.0)
        meta_conf = meta.get("confidence", 0.0)

        overall_confidence = min(1.0, cloning_conf * 0.6 + ela_conf * 0.3 + meta_conf * 0.4)

        # --- Consolidar resultados ---
        results = {
            "pre": pre,
            "suspicious_mask": clon.get("suspicious_mask"),
            "cloning_count": clon.get("cloning_count"),
            "cloning_confidence": cloning_conf,
            "ela_image": comp.get("ela_image"),
            "ela_mask": comp.get("ela_mask"),
            "ela_confidence": ela_conf,
            "metadata": meta,
            "overall_confidence": overall_confidence
        }

        # --- Generar visualización de regiones sospechosas ---
        overlay = img_bgr.copy()
        suspicious_mask = clon.get("suspicious_mask")

        os.makedirs("validation_outputs", exist_ok=True)

        if suspicious_mask is not None and np.any(suspicious_mask):
            print(" Se detectaron regiones sospechosas, generando overlay...")
            mask_uint8 = (suspicious_mask * 255).astype(np.uint8) if suspicious_mask.dtype != np.uint8 else suspicious_mask
            contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(overlay, contours, -1, (0, 0, 255), 2)
            overlay = cv2.addWeighted(img_bgr, 0.7, overlay, 0.3, 0)

            # Guardar copia visual para depuración
            cv2.imwrite("validation_outputs/debug_overlay.jpg", overlay)
            print(" Imagen de sospechas guardada en validation_outputs/debug_overlay.jpg")
        else:
            print(" No se detectaron regiones sospechosas o máscara vacía")
            overlay = img_bgr

        # --- Convertir imagen resultante a Base64 para API ---
        _, buffer = cv2.imencode(".png", overlay)
        image_base64 = base64.b64encode(buffer).decode("utf-8")

        # --- Generar reporte textual ---
        report = self.reporter.generate(img_bgr, results)

        # --- Asegurar que el reporte incluya la imagen ---
        if isinstance(report, dict):
            report["image_base64"] = image_base64
        else:
            report = {"text_report": report, "image_base64": image_base64}

        print(" Claves en el reporte:", list(report.keys()))

        results["report"] = report
        return results
