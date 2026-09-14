import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from Backend.src.core.cache import check_cache_connection
import logging
import time
from fastapi import Request
logger = logging.getLogger(__name__)

from Backend.database import Base, SessionLocal, engine
from Backend.src.core.security import decode_access_token
from Backend.src.repositories.audit_repository import AuditRepository
from Backend.src.scripts.create_admin import create_admin

# Auto-create all tables in PostgreSQL
Base.metadata.create_all(bind=engine)

# Import all routers
from Backend.src.routes.admin_routes import router as admin_router
from Backend.src.routes.announcement_routes import router as announcement_router
from Backend.src.routes.assignment_routes import router as assignment_router
from Backend.src.routes.audit_routes import router as audit_router
from Backend.src.routes.auth_routes import router as auth_router
from Backend.src.routes.course_routes import router as course_router
from Backend.src.routes.discussion_routes import router as discussion_router
from Backend.src.routes.enrollment_routes import router as enrollment_router
from Backend.src.routes.lesson_routes import router as lesson_router
from Backend.src.routes.module_routes import router as module_router
from Backend.src.routes.notification_routes import router as notification_router
from Backend.src.routes.progress_routes import router as progress_router
from Backend.src.routes.report_routes import router as report_router
from Backend.src.routes.quiz_routes import router as quiz_router
from Backend.src.routes.session_routes import router as session_router
from fastapi.middleware.cors import CORSMiddleware
from Backend.src.routes.student_routes import dashboard_router as student_dashboard_router, router as student_router
from Backend.src.routes.teacher_routes import dashboard_router as teacher_dashboard_router, router as teacher_router
from Backend.src.routes.file_routes import router as file_router


app = FastAPI(
    title="LMS API",
    description="Full-Featured Learning Management System REST API built with FastAPI and PostgreSQL",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://localhost:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):

    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start_time

    logger.info(
        "%s %s - Status: %s - Time: %.4fs",
        request.method,
        request.url.path,
        response.status_code,
        process_time
    )

    response.headers["X-Process-Time"] = f"{process_time:.4f}"

    if request.method in {"POST", "PUT", "PATCH", "DELETE"} and response.status_code < 400:
        path_parts = [part for part in request.url.path.split("/") if part]
        excluded = {"audit-logs", "notifications", "progress"}
        if path_parts and path_parts[0] not in excluded:
            authorization = request.headers.get("authorization", "")
            if authorization.lower().startswith("bearer "):
                payload = decode_access_token(authorization.split(" ", 1)[1])
                uid = payload.get("sub") if payload else None
                if uid:
                    action = {"POST": "created", "PUT": "updated", "PATCH": "updated", "DELETE": "deleted"}[request.method]
                    if path_parts[:2] == ["admin", "invite-teacher"]:
                        action = "invited"
                    entity_type = {
                        "courses": "course",
                        "assignments": "assignment",
                        "sessions": "session",
                        "quizzes": "quiz",
                        "enrollments": "enrollment",
                        "admin": "admin",
                    }.get(path_parts[0], path_parts[0].replace("-", "_"))
                    entity_id = next((part for part in path_parts[1:] if part.isdigit()), None)
                    audit_db = SessionLocal()
                    try:
                        AuditRepository.log(audit_db, uid, action, entity_type, entity_id)
                    except Exception:
                        audit_db.rollback()
                        logger.exception("Unable to record audit activity")
                    finally:
                        audit_db.close()

    return response
@app.on_event("startup")
def startup_event():
    if check_cache_connection():
        print("Valkey connected successfully")
    else:
        print("Valkey connection failed")
    create_admin()

# Ensure uploads directory exists and mount for static file access
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
def home():
    return {
        "status": "online",
        "message": "LMS Backend API is running successfully",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


# Register All Core and Advanced Routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(student_router)
app.include_router(teacher_router)
app.include_router(student_dashboard_router)
app.include_router(teacher_dashboard_router)
app.include_router(course_router)
app.include_router(enrollment_router)
app.include_router(module_router)
app.include_router(lesson_router)
app.include_router(progress_router)
app.include_router(report_router)
app.include_router(assignment_router)
app.include_router(quiz_router)
app.include_router(session_router)
app.include_router(discussion_router)
app.include_router(announcement_router)
app.include_router(notification_router)
app.include_router(audit_router)
app.include_router(file_router)
