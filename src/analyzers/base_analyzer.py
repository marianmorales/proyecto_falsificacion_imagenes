from abc import ABC, abstractmethod

class BaseAnalyzer(ABC):
    """
    Clase base abstracta para todos los analizadores.
    Cada analizador debe implementar el método analyze().
    """

    @abstractmethod
    def analyze(self, image, info=None):
        """
        Método que realiza el análisis de la imagen.
        Debe ser implementado por cada clase hija.

        Parámetros:
        -----------
        image : np.ndarray
            Imagen en formato OpenCV (BGR).
        info : dict, opcional
            Información adicional (como ruta del archivo o metadatos).

        Retorna:
        --------
        dict
            Resultados del análisis (pueden incluir máscaras, valores o métricas).
        """
        pass
