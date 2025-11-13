from .base_analyzer import BaseAnalyzer
import piexif
import cv2
import io

class MetadataAnalyzer(BaseAnalyzer):
    """
    Analizador de metadatos EXIF avanzado.
    Detecta software de edición o IA generativa
    y evalúa la confianza del origen de la imagen.
    """

    def __init__(self):
        self.ai_keywords = [
            "midjourney", "dalle", "openai", "stable diffusion",
            "dreamstudio", "leonardo ai", "runway", "bing image creator",
            "ai generated", "artbreeder", "craiyon", "deepai"
        ]

        self.edit_keywords = [
            "photoshop", "gimp", "lightroom", "snapseed",
            "canva", "pixlr", "paint", "adobe", "corel"
        ]

    def analyze(self, image, info=None):
        meta = {}
        ai_flag = False
        edited_flag = False
        confidence = 0.0

        try:
            # --- Cargar EXIF desde archivo si está disponible ---
            if isinstance(info, dict) and info.get("filepath"):
                exif_dict = piexif.load(info["filepath"])

            else:
                # Si no hay filepath, convertir imagen de cv2 a bytes y analizar EXIF desde memoria
                success, buffer = cv2.imencode(".jpg", image)
                if not success:
                    raise ValueError("Error al codificar la imagen para análisis EXIF")
                exif_dict = piexif.load(io.BytesIO(buffer.tobytes()))

            zeroth = exif_dict.get("0th", {})
            software = zeroth.get(piexif.ImageIFD.Software, b'').decode('utf-8', errors='ignore').lower()
            model = zeroth.get(piexif.ImageIFD.Model, b'').decode('utf-8', errors='ignore').lower()
            make = zeroth.get(piexif.ImageIFD.Make, b'').decode('utf-8', errors='ignore').lower()

            meta["software"] = software or "Desconocido"
            meta["camera_model"] = model or "Desconocido"
            meta["make"] = make or "Desconocido"

            # --- Detección de IA o software de edición ---
            for keyword in self.ai_keywords:
                if keyword in software or keyword in model or keyword in make:
                    ai_flag = True
                    break

            for keyword in self.edit_keywords:
                if keyword in software or keyword in model or keyword in make:
                    edited_flag = True
                    break

            # --- Asignar nivel de confianza según hallazgo ---
            if ai_flag:
                confidence = 1.0
                meta["source"] = "Imagen generada o modificada por IA"

            elif edited_flag:
                confidence = 0.9
                meta["source"] = "Imagen editada en software de edición"

            elif model or make:
                confidence = 0.7
                meta["source"] = "Imagen probablemente original (dispositivo físico)"

            else:
                confidence = 0.4
                meta["source"] = "Sin datos EXIF válidos"

        except Exception as e:
            meta["error"] = str(e)
            meta["software"] = "Desconocido"
            meta["camera_model"] = "No detectado"
            meta["make"] = "Desconocido"
            meta["source"] = "No se pudieron leer metadatos"
            confidence = 0.0

        # --- Resultado final ---
        meta["ai_flag"] = ai_flag
        meta["edited_flag"] = edited_flag
        meta["confidence"] = round(confidence, 2)

        return meta
