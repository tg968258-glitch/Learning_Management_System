import io
from fastapi.testclient import TestClient

from Backend.src.api_main import app
from Backend.database import SessionLocal
from Backend.src.repositories.user_repository import UserRepository
from Backend.src.repositories.course_repository import CourseRepository

client = TestClient(app)


def test_repository_sanity_checks():
    db = SessionLocal()
    try:
        users = UserRepository.get_all(db)
        assert isinstance(users, list)
        courses = CourseRepository.get_all(db)
        assert isinstance(courses, list)
    finally:
        db.close()


def test_upload_routes_exist_in_openapi():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    paths = schema["paths"]

    # Check new PDF upload routes
    assert "/assignments/{assignment_id}/submit-file" in paths
    assert "/lessons/{lesson_id}/resources/upload-pdf" in paths
    assert "/uploads" in app.routes or any(r.path.startswith("/uploads") for r in app.routes)


def test_submit_file_validation_without_auth():
    # Calling submit-file without auth should return 401 Unauthorized
    response = client.post("/assignments/1/submit-file")
    assert response.status_code == 401


if __name__ == "__main__":
    test_repository_sanity_checks()
    test_upload_routes_exist_in_openapi()
    test_submit_file_validation_without_auth()
    print("All upload and repository tests passed!")
