import cv2
import numpy as np
from src.analyzers.base_analyzer import BaseAnalyzer

class CloningORBAnalyzer(BaseAnalyzer):
    """Analizador basado en ORB que detecta posibles regiones clonadas."""

    def __init__(self, block_size=32, match_threshold=25, texture_threshold=1.5):
        super().__init__()
        self.block_size = block_size
        self.match_threshold = match_threshold
        self.texture_threshold = texture_threshold

    def analyze(self, image):
        if image is None or image.size == 0:
            return {"cloning_count": 0, "confidence": 0.0}

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        orb = cv2.ORB_create(nfeatures=1500, scaleFactor=1.2)
        keypoints, descriptors = orb.detectAndCompute(gray, None)

        if descriptors is None or len(descriptors) < 10:
            return {"cloning_count": 0, "confidence": 0.0}

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(descriptors, descriptors)
        matches = [m for m in matches if m.distance < 45 and m.queryIdx != m.trainIdx]

        mask = np.zeros_like(gray, dtype=np.uint8)
        h, w = gray.shape[:2]
        good_points = 0

        for m in matches:
            pt1 = tuple(np.round(keypoints[m.queryIdx].pt).astype(int))
            pt2 = tuple(np.round(keypoints[m.trainIdx].pt).astype(int))
            if np.linalg.norm(np.array(pt1) - np.array(pt2)) < self.block_size:
                continue
            y, x = pt1
            y1, y2 = max(0, y-8), min(h, y+8)
            x1, x2 = max(0, x-8), min(w, x+8)
            patch = gray[y1:y2, x1:x2]
            if patch.size == 0:
                continue
            std_dev = np.std(patch)
            if std_dev < self.texture_threshold:
                continue
            cv2.circle(mask, pt1, 5, 255, -1)
            cv2.circle(mask, pt2, 5, 255, -1)
            good_points += 1

        cloning_pixels = int(np.sum(mask > 0))
        total_pixels = gray.size
        ratio = cloning_pixels / total_pixels
        confidence = min(1.0, ratio * 100 + (good_points / 500))

        return {
            "suspicious_mask": mask,
            "cloning_count": cloning_pixels,
            "confidence": round(float(confidence), 2)
        }
