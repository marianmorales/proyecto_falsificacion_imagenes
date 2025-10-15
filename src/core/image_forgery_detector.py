import cv2
from src.analyzers.preprocessing_analyzer import PreprocessingAnalyzer
from src.analyzers.cloning_analyzer import CloningAnalyzer
from src.analyzers.compression_analyzer import CompressionAnalyzer
from src.analyzers.metadata_analyzer import MetadataAnalyzer
from src.report.report_generator import ReportGenerator

class ImageForgeryDetector:
    """
    Clase principal que coordina los análisis de manipulación de imagen.
    """

    def __init__(self):
        self.pre = PreprocessingAnalyzer()
        self.clone = CloningAnalyzer(block_size=32)
        self.comp = CompressionAnalyzer(quality=90)
        self.meta = MetadataAnalyzer()
        self.reporter = ReportGenerator()

    def analyze_from_path(self, filepath):
        """
        Carga una imagen desde el disco y la analiza.
        """
        img = cv2.imread(filepath)
        return self._analyze(img, info={"filepath": filepath})

    def analyze_from_array(self, bgr_image):
        """
        Analiza una imagen recibida como array (por ejemplo, desde Flask).
        """
        return self._analyze(bgr_image, info=None)

    def _analyze(self, img_bgr, info=None):
        pre = self.pre.analyze(img_bgr)
        clon = self.clone.analyze(img_bgr)
        comp = self.comp.analyze(img_bgr)
        meta = self.meta.analyze(img_bgr, info=info)

        cloning_conf = clon.get("confidence", 0.0)
        ela_conf = comp.get("confidence", 0.0)
        meta_conf = meta.get("confidence", 0.0)

        overall_confidence = min(1.0, cloning_conf * 0.6 + ela_conf * 0.3 + meta_conf * 0.4)

        results = {
            "pre": pre,
            "suspicious_mask": clon.get("suspicious_mask"),
            "cloning_count": clon.get("cloning_count"),
            "cloning_confidence": cloning_conf,
            "ela_image": comp.get("ela_image"),
            "ela_mask": comp.get("ela_mask"),
            "ela_confidence": ela_conf,
            "metadata": meta,
            "overall_confidence": overall_confidence
        }

        report = self.reporter.generate(img_bgr, results)
        results["report"] = report
        return results
