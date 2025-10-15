from .base_analyzer import BaseAnalyzer
import piexif

class MetadataAnalyzer(BaseAnalyzer):
    """
    Analizador de metadatos EXIF:
    Examina información interna del archivo (modelo de cámara, software de edición, etc.)
    para detectar posibles manipulaciones.
    """

    def analyze(self, image, info=None):
        meta = {}

        try:
            # Solo se puede extraer EXIF si se conoce la ruta del archivo
            if isinstance(info, dict) and info.get("filepath"):
                filepath = info["filepath"]
                exif_dict = piexif.load(filepath)

                # Extraer campos comunes del bloque "0th" (datos generales)
                zeroth = exif_dict.get("0th", {})
                software = zeroth.get(piexif.ImageIFD.Software, b'').decode('utf-8', errors='ignore')
                model = zeroth.get(piexif.ImageIFD.Model, b'').decode('utf-8', errors='ignore')

                # Cargar resultados
                meta["software"] = software
                meta["camera_model"] = model

                # Heurística simple: si hay software distinto a cámara, se marca sospechoso
                edited = bool(software)
                confidence = 0.9 if edited else 0.0

                meta["edited_flag"] = edited
                meta["confidence"] = confidence

            else:
                meta["note"] = "No se proporcionó filepath, no se puede analizar EXIF"
                meta["confidence"] = 0.0

        except Exception as e:
            meta["error"] = str(e)
            meta["confidence"] = 0.0

        return meta
