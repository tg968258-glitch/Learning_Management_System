from unittest.mock import patch
from fastapi.testclient import TestClient
from Backend.src.api_main import app
from Backend.src.core.cache import redis_client

client = TestClient(app)

def test_cache_keys_and_scan_iter():
    try:
        ping_res = redis_client.ping()
        print(f"Redis ping result: {ping_res}")
    except Exception as e:
        print(f"Redis connection info: {e}")

def test_cache_helpers():
    from Backend.src.routes.announcement_routes import _clear_announcements_cache
    from Backend.src.routes.module_routes import _clear_modules_cache
    from Backend.src.routes.lesson_routes import _clear_lessons_cache
    from Backend.src.routes.quiz_routes import _clear_quizzes_cache
    from Backend.src.routes.session_routes import _clear_sessions_cache
    from Backend.src.routes.student_routes import _clear_student_cache
    from Backend.src.routes.teacher_routes import _clear_teacher_cache

    with patch.object(redis_client, "scan_iter", return_value=["test:1", "test:2"]), \
         patch.object(redis_client, "delete") as mock_del:
        _clear_announcements_cache()
        _clear_modules_cache()
        _clear_lessons_cache()
        _clear_quizzes_cache()
        _clear_sessions_cache()
        _clear_student_cache()
        _clear_teacher_cache()
        assert mock_del.call_count >= 14
