from flask import Flask, request, jsonify, render_template_string
import numpy as np
import cv2
from src.core.image_forgery_detector import ImageForgeryDetector


app = Flask(__name__)
detector = ImageForgeryDetector()

# Interfaz HTML simple
INDEX_HTML = """
<!doctype html>
<title>Detección de Manipulación - MVP</title>
<h2>Subir imagen para analizar</h2>
<form method=post enctype=multipart/form-data action="/analyze">
  <input type=file name=file>
  <input type=submit value="Analizar">
</form>
{% if result %}
  <h3>Reporte</h3>
  <img src="data:image/png;base64,{{ result['image_base64'] }}" style="max-width:80%;">
  <pre>{{ result['text_report'] | tojson(indent=2) }}</pre>
{% endif %}
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(INDEX_HTML)

@app.route("/analyze", methods=["POST"])
def analyze():
    f = request.files.get("file")
    if not f:
        return "No se subió ningún archivo", 400

    data = f.read()
    nparr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    res = detector.analyze_from_array(img)
    return render_template_string(INDEX_HTML, result=res["report"])

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "No se subió archivo"}), 400

    data = f.read()
    nparr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    res = detector.analyze_from_array(img)

    return jsonify({
        "overall_confidence": res.get("overall_confidence"),
        "report": res.get("report")["text_report"],
        "image_base64": res.get("report")["image_base64"]
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
