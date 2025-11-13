import base64
import cv2
import numpy as np
import tempfile
import os
from flask import Flask, render_template_string, request
from src.core.image_forgery_detector import ImageForgeryDetector

app = Flask(__name__)
detector = ImageForgeryDetector()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Detector de Falsificación de Imágenes</title>
<style>
  body {
    font-family: Arial, sans-serif;
    background-color: #0e1117;
    color: #e0e0e0;
    text-align: center;
    padding: 30px;
  }
  h1 { color: #00bcd4; }
  .container {
    max-width: 800px;
    margin: auto;
    background: #1c1f26;
    border-radius: 16px;
    padding: 25px;
    box-shadow: 0 0 15px rgba(0,0,0,0.5);
  }
  .image-box {
    margin: 20px auto;
    border: 5px solid {{ border_color }};
    border-radius: 10px;
    display: inline-block;
    overflow: hidden;
  }
  img {
    max-width: 100%;
    height: auto;
    display: block;
  }
  .bar-container {
    background: #333;
    border-radius: 10px;
    overflow: hidden;
    height: 20px;
    margin-top: 10px;
  }
  .bar {
    height: 100%;
    width: {{ (overall_confidence * 100)|round(1) }}%;
    background: {{ border_color }};
    transition: width 0.4s ease;
  }
  .metadata {
    text-align: left;
    margin-top: 20px;
    background: #2a2f3a;
    padding: 15px;
    border-radius: 10px;
  }
  .metadata h3 {
    color: #00bcd4;
    margin-bottom: 8px;
  }
  .metadata p {
    margin: 4px 0;
  }
  .btn {
    background-color: #00bcd4;
    border: none;
    padding: 10px 20px;
    color: #fff;
    font-size: 16px;
    border-radius: 8px;
    cursor: pointer;
  }
  .btn:hover {
    background-color: #0097a7;
  }
</style>
</head>
<body>
  <div class="container">
    <h1> Detector de Falsificación de Imágenes</h1>

    <form action="/analyze" method="POST" enctype="multipart/form-data">
      <input type="file" name="image" accept="image/*" required>
      <br><br>
      <button type="submit" class="btn">Analizar imagen</button>
    </form>

    {% if result %}
      <hr>
      <div class="image-box">
        <img src="data:image/png;base64,{{ result['report']['image_base64'] }}" alt="Resultado">
      </div>

      <h2>Informe General</h2>
      <p><strong>Confianza de clonación:</strong> {{ result['cloning_confidence'] }}</p>
      <p><strong>Regiones clonadas detectadas:</strong> {{ result['cloning_count'] }}</p>
      <p><strong>ELA (Compresión):</strong> {{ result['ela_confidence'] }}</p>
      <p><strong>Nivel general de sospecha:</strong>
         {% if result['overall_confidence'] > 0.7 %} Alta
         {% elif result['overall_confidence'] > 0.4 %} Media
         {% else %} Baja {% endif %}
      </p>

      <div class="bar-container">
        <div class="bar"></div>
      </div>

      <div class="metadata">
        <h3>Metadatos</h3>
        <p><strong>Software:</strong> {{ result['metadata'].get('software', 'Desconocido') }}</p>
        <p><strong>Modelo de cámara:</strong> {{ result['metadata'].get('camera_model', 'No detectado') }}</p>
        <p><strong>Fabricante:</strong> {{ result['metadata'].get('make', 'Desconocido') }}</p>
        <p><strong>Fuente estimada:</strong> {{ result['metadata'].get('source', 'No se pudieron leer metadatos') }}</p>
        <p><strong>Bandera de IA:</strong>
           {% if result['metadata'].get('ai_flag', False) %} Detectada {% else %} No detectada {% endif %}
        </p>
        <p><strong>Edición detectada:</strong>
           {% if result['metadata'].get('edited_flag', False) %} Editada {% else %} Original {% endif %}
        </p>
        <p><strong>Confianza de metadatos:</strong> {{ result['metadata'].get('confidence', 0.0) }}</p>
      </div>
    {% endif %}
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_TEMPLATE, result=None, border_color="#00bcd4", overall_confidence=0)

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["image"]

    # Guardar archivo temporal para preservar los metadatos EXIF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        temp_path = tmp.name
        file.save(temp_path)

    try:
        # Analizar imagen con ruta temporal
        results = detector.analyze_from_path(temp_path)
    finally:
        # Eliminar el archivo temporal luego del análisis
        os.remove(temp_path)

    overall_confidence = results.get("overall_confidence", 0.0)

    # Determinar color de borde según el nivel de sospecha
    if overall_confidence > 0.7:
        border_color = "#ff4444"  # rojo
    elif overall_confidence > 0.4:
        border_color = "#ffbb33"  # amarillo
    else:
        border_color = "#00C851"  # verde

    return render_template_string(
        HTML_TEMPLATE,
        result=results,
        border_color=border_color,
        overall_confidence=overall_confidence
    )

if __name__ == "__main__":
    app.run(debug=True)
