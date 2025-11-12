import cv2
import numpy as np
import os

class PreprocessingAnalyzer:
    """
    Aplica técnicas de preprocesamiento sobre una imagen
    para mejorar la detección de falsificaciones.
    """

    def __init__(self, target_size=(512, 512)):
        self.target_size = target_size

    def _resize_adaptive(self, image, target_size):
        """
        Escala la imagen sin deformarla, rellenando con bordes negros si es necesario.
        """
        h, w = image.shape[:2]
        scale = min(target_size[0] / h, target_size[1] / w)
        new_size = (int(w * scale), int(h * scale))
        resized = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

        # Rellenar para alcanzar tamaño exacto
        delta_w = target_size[1] - new_size[0]
        delta_h = target_size[0] - new_size[1]
        top, bottom = delta_h // 2, delta_h - (delta_h // 2)
        left, right = delta_w // 2, delta_w - (delta_w // 2)
        color = [0, 0, 0]
        padded = cv2.copyMakeBorder(resized, top, bottom, left, right,
                                    cv2.BORDER_CONSTANT, value=color)
        return padded

    def analyze(self, image_input):
        """
        Ejecuta el preprocesamiento sobre una imagen dada.
        Puede recibir una ruta (str) o una imagen (array de NumPy).
        """

        # Si se pasa una ruta, cargar la imagen
        if isinstance(image_input, (str, bytes, os.PathLike)):
            if not os.path.exists(image_input):
                raise FileNotFoundError(f"No se encontró la imagen: {image_input}")
            image = cv2.imread(image_input)
            if image is None:
                raise ValueError(f"No se pudo cargar la imagen desde: {image_input}")
        else:
            # Si ya es una imagen (array NumPy), usarla directamente
            image = image_input

        # 1. Conversión a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 2. Redimensionado adaptativo
        gray = self._resize_adaptive(gray, self.target_size)

        # 3. Equalización de histograma adaptativa (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        equalized = clahe.apply(gray)

        # 4. Desenfoque Gaussiano suave
        blurred = cv2.GaussianBlur(equalized, (3, 3), 0)

        # 5. Detección de bordes (Sobel)
        sobelx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
        edges = cv2.magnitude(sobelx, sobely)
        edges = np.uint8(np.clip(edges, 0, 255))

        # 6. Normalización final (0–1)
        normalized = cv2.normalize(edges.astype("float32"), None, 0.0, 1.0, cv2.NORM_MINMAX)

        #  Guardar resultado del preprocesamiento
        os.makedirs("validation_outputs", exist_ok=True)
        output_name = os.path.basename(image_input if isinstance(image_input, str) else "array_input")
        output_name = os.path.splitext(output_name)[0]
        output_path = f"validation_outputs/preprocessed_{output_name}.jpg"
        cv2.imwrite(output_path, (normalized * 255).astype(np.uint8))

        print(f" Imagen preprocesada guardada en: {output_path}")
        return normalized
