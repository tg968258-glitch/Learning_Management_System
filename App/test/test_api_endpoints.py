from fastapi.testclient import TestClient

from Backend.src.api_main import app

client = TestClient(app)

def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "LMS" in data["message"]

def test_openapi_docs():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    paths = schema["paths"]
    
    # Check that core domains exist
    assert "/auth/login" in paths
    assert "/students/" in paths
    assert "/teachers/" in paths
    assert "/courses/" in paths
    assert "/enrollments/" in paths
    assert "/modules/" in paths
    assert "/lessons/" in paths
    assert "/progress/lesson/{lesson_id}" in paths
    assert "/assignments/" in paths
    assert "/quizzes/" in paths
    assert "/sessions/" in paths
    assert "/discussions/" in paths
    assert "/announcements/" in paths
    assert "/notifications/my-notifications" in paths
    assert "/audit-logs/" in paths
    print(f"Total OpenAPI API Paths verified: {len(paths)}")

if __name__ == "__main__":
    test_home_endpoint()
    test_openapi_docs()
    print("All smoke tests passed!")
