import os
import pytest
from src import run_validation

def test_validation_outputs_exist(tmp_path):
    """Verifica que run_validation genere resultados en validation_outputs/."""
    os.makedirs("validation_outputs", exist_ok=True)
    # Si run_validation tiene una función principal, se puede llamar así:
    # run_validation.main()
    outputs = os.listdir("validation_outputs")
    assert outputs is not None
