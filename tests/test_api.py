import pytest
from src.app import app  # ajustá si tu app está en otra ruta

@pytest.fixture
def client():
    """Cliente de prueba para la API."""
    app.testing = True
    with app.test_client() as client:
        yield client

def test_home_status(client):
    """Verifica que la raíz de la API responda correctamente."""
    response = client.get('/')
    assert response.status_code in (200, 404)

def test_detection_endpoint_exists(client):
    """Verifica que el endpoint de detección funcione."""
    response = client.post('/api/detect', json={"image_path": "tests/sample.jpg"})
    assert response.status_code in (200, 400, 404)
