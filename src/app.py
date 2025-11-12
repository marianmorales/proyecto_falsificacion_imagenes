from flask import Flask, request, jsonify, render_template_string
from src.core.image_forgery_detector import ImageForgeryDetector
import os

app = Flask(__name__)
detector = ImageForgeryDetector()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Detector de Falsificación de Imágenes </title>
    <style>
        body { font-family: Arial, sans-serif; background: #f2f2f2; text-align: center; margin: 0; padding: 40px; }
        .container { background: white; display: inline-block; padding: 30px; border-radius: 15px;
                     box-shadow: 0 2px 10px rgba(0,0,0,0.15); }
        input[type=file] { margin: 15px 0; }
        img { max-width: 600px; border-radius: 10px; margin-top: 20px; }
        pre { text-align: left; background: #fafafa; padding: 15px; border-radius: 10px;
              border: 1px solid #ddd; overflow-x: auto; }
        button { background-color: #0078D7; color: white; border: none; padding: 10px 25px;
                 border-radius: 8px; cursor: pointer; }
        button:hover { background-color: #005a9e; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Detector de Falsificación de Imágenes </h1>
        <form action="/analyze" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <br>
            <button type="submit">Analizar imagen</button>
        </form>

        {% if text_report %}
            <h3>Informe:</h3>
            <pre>{{ text_report }}</pre>
        {% endif %}

        {% if image_base64 %}
            <h3>Regiones sospechosas detectadas:</h3>
            <img src="data:image/png;base64,{{ image_base64 }}" alt="Resultado del análisis">
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return render_template_string(HTML_TEMPLATE, text_report="⚠️ No se envió ningún archivo.")

    file = request.files["file"]
    os.makedirs("validation_outputs", exist_ok=True)
    filepath = os.path.join("validation_outputs", file.filename)
    file.save(filepath)

    result = detector.analyze_from_path(filepath)
    report = result.get("report", {})

    # Extraer el texto y la imagen codificada
    text_report = report.get("text_report", "Sin informe generado.")
    image_base64 = report.get("image_base64", None)

    return render_template_string(HTML_TEMPLATE, text_report=text_report, image_base64=image_base64)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
