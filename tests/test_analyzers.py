import pytest
from src.analyzers.preprocessing_analyzer import PreprocessingAnalyzer
from src.analyzers.cloning_orb_analyzer import CloningORBAnalyzer



def test_preprocessing_creation():
    """Verifica que el analizador de preprocesamiento se pueda crear."""
    analyzer = PreprocessingAnalyzer()
    assert analyzer is not None

def test_cloning_orb_creation():
    """Verifica que el analizador ORB se pueda crear."""
    analyzer = CloningORBAnalyzer()
    assert analyzer is not None
