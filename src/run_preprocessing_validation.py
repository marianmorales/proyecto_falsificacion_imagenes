import os
import glob
from src.analyzers.preprocessing_analyzer import PreprocessingAnalyzer

def main(input_folder="test_images", output_folder="validation_outputs"):
    """
    Ejecuta el preprocesamiento sobre todas las imágenes de una carpeta.
    Guarda los resultados preprocesados para inspección visual.
    """
    print(f" Iniciando preprocesamiento en carpeta: {input_folder}")

    os.makedirs(output_folder, exist_ok=True)
    image_paths = []
    for ext in ("*.jpg", "*.jpeg", "*.png"):
        image_paths.extend(glob.glob(os.path.join(input_folder, ext)))

    if not image_paths:
        print(" No se encontraron imágenes en la carpeta especificada.")
        return

    preprocessor = PreprocessingAnalyzer()

    for img_path in image_paths:
        try:
            print(f" Procesando: {os.path.basename(img_path)} ...")
            preprocessor.analyze(img_path)
        except Exception as e:
            print(f" Error procesando {img_path}: {e}")

    print(f" Preprocesamiento completado. Resultados guardados en: {output_folder}")

if __name__ == "__main__":
    main()
