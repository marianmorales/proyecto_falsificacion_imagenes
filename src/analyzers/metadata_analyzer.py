from .base_analyzer import BaseAnalyzer
import piexif

class MetadataAnalyzer(BaseAnalyzer):
    """
    Analizador de metadatos EXIF avanzado.
    Extrae información del archivo (modelo de cámara, software de edición, IA generativa, etc.)
    para detectar posibles manipulaciones o generación artificial.
    """

    def __init__(self):
        # Lista de softwares y etiquetas que suelen aparecer en imágenes generadas por IA
        self.ai_keywords = [
            "midjourney", "dalle", "openai", "stable diffusion",
            "dreamstudio", "leonardo ai", "runway", "bing image creator",
            "ai generated", "artbreeder", "craiyon", "deepai"
        ]

        # Lista de softwares comunes de edición
        self.edit_keywords = [
            "photoshop", "gimp", "lightroom", "snapseed",
            "canva", "pixlr", "paint", "adobe", "corel"
        ]

    def analyze(self, image, info=None):
        meta = {}
        ai_flag = False
        edited_flag = False

        try:
            # Asegurar que tenemos filepath
            if isinstance(info, dict) and info.get("filepath"):
                filepath = info["filepath"]
                exif_dict = piexif.load(filepath)

                # Obtener bloque "0th" (datos generales EXIF)
                zeroth = exif_dict.get("0th", {})
                software = zeroth.get(piexif.ImageIFD.Software, b'').decode('utf-8', errors='ignore').lower()
                model = zeroth.get(piexif.ImageIFD.Model, b'').decode('utf-8', errors='ignore').lower()
                make = zeroth.get(piexif.ImageIFD.Make, b'').decode('utf-8', errors='ignore').lower()

                meta["software"] = software or "Desconocido"
                meta["camera_model"] = model or "Desconocido"
                meta["make"] = make or "Desconocido"

                # Detección de IA o software de edición
                for keyword in self.ai_keywords:
                    if keyword in software or keyword in model or keyword in make:
                        ai_flag = True
                        break

                for keyword in self.edit_keywords:
                    if keyword in software or keyword in model or keyword in make:
                        edited_flag = True
                        break

                # Asignar nivel de confianza según el hallazgo
                if ai_flag:
                    confidence = 1.0
                    meta["source"] = "Imagen generada o modificada por IA"
                elif edited_flag:
                    confidence = 0.9
                    meta["source"] = "Imagen editada en software de edición"
                elif software or model or make:
                    confidence = 0.2
                    meta["source"] = "Imagen probablemente original (dispositivo físico)"
                else:
                    confidence = 0.0
                    meta["source"] = "Sin datos EXIF válidos"

            else:
                meta["note"] = "No se proporcionó filepath, no se puede analizar EXIF"
                confidence = 0.0

        except Exception as e:
            meta["error"] = str(e)
            confidence = 0.0

        meta["ai_flag"] = ai_flag
        meta["edited_flag"] = edited_flag
        meta["confidence"] = confidence

        return meta
