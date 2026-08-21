from fastapi.testclient import TestClient

from Backend.src.api_main import app

client = TestClient(app)


def test_get_students_unauthorized():
    # Calling /students/ without token must be rejected with 401 Unauthorized
    response = client.get("/students/")
    assert response.status_code == 401