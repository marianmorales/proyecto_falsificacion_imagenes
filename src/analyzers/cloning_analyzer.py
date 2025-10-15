import cv2
import numpy as np
from .base_analyzer import BaseAnalyzer
from collections import defaultdict

class CloningAnalyzer(BaseAnalyzer):
    """
    Analizador de clonación:
    Divide la imagen en bloques y busca regiones duplicadas
    que puedan indicar manipulación o clonación.
    """

    def __init__(self, block_size=32):
        """
        Parámetros:
        ------------
        block_size : int
            Tamaño de los bloques en píxeles.
        """
        self.block_size = block_size

    def analyze(self, image, info=None):
        # Convertir a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        bs = self.block_size

        # Diccionario para guardar descriptores de cada bloque
        hashes = defaultdict(list)
        # Máscara para marcar las zonas sospechosas
        suspicious_mask = np.zeros_like(gray, dtype=np.uint8)

        # Recorremos la imagen por bloques
        for y in range(0, h - bs + 1, bs):
            for x in range(0, w - bs + 1, bs):
                block = gray[y:y+bs, x:x+bs]
                # Descriptor simple (promedio y desviación)
                desc = (int(block.mean()), int(block.std()))
                hashes[desc].append((x, y))

        # Buscar duplicados
        duplications = []
        for desc, coords in hashes.items():
            if len(coords) > 1:
                duplications.extend(coords)
                for (x, y) in coords:
                    suspicious_mask[y:y+bs, x:x+bs] = 255

        # Calcular una "confianza" heurística basada en la cantidad de duplicaciones
        confidence = min(1.0, len(duplications) / 20.0)

        return {
            "suspicious_mask": suspicious_mask,
            "cloning_count": len(duplications),
            "confidence": confidence
        }
