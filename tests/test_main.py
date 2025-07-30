from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_get_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Response": "This is the home page"}

def test_db_connection():
    response = client.get("/test-db")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
