import cv2
import numpy as np
import time
from src.analyzers.preprocessing_analyzer import PreprocessingAnalyzer
from src.analyzers.cloning_analyzer import CloningAnalyzer
from src.analyzers.compression_analyzer import CompressionAnalyzer
from src.analyzers.metadata_analyzer import MetadataAnalyzer
from src.report.report_generator import ReportGenerator


class ImageForgeryDetector:
    """
    Clase principal que coordina los análisis de manipulación de imágenes.
    """

    def __init__(self):
        self.pre = PreprocessingAnalyzer()
        self.clone = CloningAnalyzer(block_size=32)
        self.comp = CompressionAnalyzer(quality=90)
        self.meta = MetadataAnalyzer()
        self.reporter = ReportGenerator()

    def analyze_from_path(self, filepath):
        """Carga una imagen desde disco y la analiza."""
        img = cv2.imread(filepath)
        return self._analyze(img, info={"filepath": filepath})

    def analyze_from_array(self, bgr_image):
        """Analiza una imagen recibida como array (por ejemplo, desde Flask)."""
        return self._analyze(bgr_image, info=None)

    def _analyze(self, img_bgr, info=None):
        if img_bgr is None:
            raise ValueError("Imagen no válida o no encontrada.")

        # --- inicio de tiempo para logging simple ---
        start_time = time.time()

        # ===== 1. PREPROCESAMIENTO =====
        pre = self.pre.analyze(img_bgr)

        # ===== 2. ANÁLISIS DE CLONACIÓN =====
        clon = self.clone.analyze(img_bgr)
        suspicious_mask = clon.get("suspicious_mask", np.zeros(img_bgr.shape[:2], np.uint8))
        cloning_count = clon.get("cloning_count", 0)
        cloning_conf = float(clon.get("confidence", 0.0))

        # ===== 3. ANÁLISIS DE COMPRESIÓN (ELA) =====
        comp = self.comp.analyze(img_bgr)
        ela_conf = float(comp.get("confidence", 0.0))

        # ===== 4. ANÁLISIS DE METADATOS =====
        meta = self.meta.analyze(img_bgr, info=info)
        meta_conf = float(meta.get("confidence", 0.0))

        # ===== 5. COMBINAR PUNTAJES (normalizado: suma de pesos = 1.0) =====
        # Pesos recomendados: clonación 0.5, ELA 0.3, metadatos 0.2
        overall_confidence = cloning_conf * 0.5 + ela_conf * 0.3 + meta_conf * 0.2
        # Opcional: asegurar rango [0,1]
        overall_confidence = max(0.0, min(1.0, overall_confidence))

        # ===== 6. GENERAR OVERLAY VISUAL =====
        overlay = img_bgr.copy()
        mask_norm = cv2.normalize(suspicious_mask, None, 0, 255, cv2.NORM_MINMAX)
        mask_colored = cv2.applyColorMap(mask_norm.astype(np.uint8), cv2.COLORMAP_JET)
        blended = cv2.addWeighted(overlay, 0.7, mask_colored, 0.3, 0)

        # === Barra de confianza visual mejorada ===
        legend_height = 60
        bar = np.zeros((legend_height, blended.shape[1], 3), dtype=np.uint8)

        for i in range(bar.shape[1]):
            ratio = i / bar.shape[1]
            if ratio < 0.5:
                g = 255
                r = int(510 * ratio)
                color_grad = (0, g, r)
            else:
                r = 255
                g = int(510 * (1 - ratio))
                color_grad = (0, g, r)
            bar[:, i] = color_grad

        # Texto centrado y legible
        cv2.putText(bar, "Baja sospecha", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(bar, "Alta sospecha", (bar.shape[1]-200, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Mostrar el SCORE GLOBAL (overall_confidence) en la barra (CORRECCIÓN)
        conf_text = f"Confianza: {overall_confidence:.2f}"
        text_size = cv2.getTextSize(conf_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
        text_x = (bar.shape[1] - text_size[0]) // 2
        cv2.putText(bar, conf_text, (text_x, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        # Unir barra + imagen
        final_display = np.vstack([blended, bar])

        # Guardar debug overlay
        try:
            cv2.imwrite("validation_outputs/debug_overlay.jpg", final_display)
            print(" Imagen de sospechas guardada en validation_outputs/debug_overlay.jpg")
        except Exception as e:
            print("Error guardando debug overlay:", e)

        # tiempo total
        end_time = time.time()
        analysis_time = round(end_time - start_time, 3)

        # ===== 7. GENERAR REPORTE =====
        results = {
            "pre": pre,
            "suspicious_mask": suspicious_mask,
            "cloning_count": cloning_count,
            "cloning_confidence": cloning_conf,
            "ela_confidence": ela_conf,
            "metadata": meta,
            "overall_confidence": overall_confidence,
            # --- LOG / trazabilidad extra solicitada ---
            "modules_used": ["preprocessing", "cloning", "ela", "metadata"],
            "analysis_time_seconds": analysis_time,
            "file_info": info
        }

        report = self.reporter.generate(img_bgr, results)
        results["report"] = report
        return results
