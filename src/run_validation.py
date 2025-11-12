import os
from src.core.image_forgery_detector import ImageForgeryDetector
import base64
from pathlib import Path
import json

INPUT_DIR = Path(__file__).parent.parent / "test_images"
OUTPUT_DIR = Path(__file__).parent.parent / "validation_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

def save_base64_image(b64, outpath):
    data = base64.b64decode(b64)
    with open(outpath, "wb") as f:
        f.write(data)

def main():
    detector = ImageForgeryDetector()
    results_summary = []

    for img_path in INPUT_DIR.glob("*.*"):
        print("Analizando:", img_path.name)
        res = detector.analyze_from_path(str(img_path))
        rep = res["report"]

        out_img = OUTPUT_DIR / f"{img_path.stem}_result.png"
        save_base64_image(rep["image_base64"], out_img)

        out_json = OUTPUT_DIR / f"{img_path.stem}_report.json"
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(rep["text_report"], f, ensure_ascii=False, indent=2)

        results_summary.append({
            "file": img_path.name,
            "out_image": str(out_img),
            "report": rep["text_report"]
        })

    summary_path = OUTPUT_DIR / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results_summary, f, ensure_ascii=False, indent=2)

    print(" Validación finalizada. Resultados en:", OUTPUT_DIR)

if __name__ == "__main__":
    main()
