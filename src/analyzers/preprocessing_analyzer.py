import cv2
import numpy as np
from .base_analyzer import BaseAnalyzer

class PreprocessingAnalyzer(BaseAnalyzer):
    """
    Analizador de preprocesamiento:
    - Convierte la imagen a escala de grises
    - Normaliza los valores de los píxeles entre 0 y 1
    """

    def analyze(self, image, info=None):
        # Convertir a escala de grises (OpenCV usa formato BGR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Normalizar valores entre 0 y 1
        norm = cv2.normalize(gray.astype('float32'), None, 0.0, 1.0, cv2.NORM_MINMAX)

        # Devolver resultados en un diccionario
        return {
            "gray": gray,
            "norm": norm
        }
