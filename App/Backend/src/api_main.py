import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from Backend.src.core.cache import check_cache_connection
import time
from fastapi import Request

from Backend.database import Base, engine

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
from Backend.src.routes.quiz_routes import router as quiz_router
from Backend.src.routes.session_routes import router as session_router
from Backend.src.routes.student_routes import router as student_router
from Backend.src.routes.teacher_routes import router as teacher_router

app = FastAPI(
    title="LMS API",
    description="Full-Featured Learning Management System REST API built with FastAPI and PostgreSQL",
    version="1.0.0"
)

@app.middleware("http")
async def request_time_middleware(request: Request, call_next):

    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    print(
        f"{request.method} {request.url.path} "
        f"completed in {process_time:.4f} seconds"
    )

    response.headers["X-Process-Time"] = str(process_time)

    return response

@app.on_event("startup")
def startup_event():
    if check_cache_connection():
        print("Valkey connected successfully")
    else:
        print("Valkey connection failed")

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
app.include_router(course_router)
app.include_router(enrollment_router)
app.include_router(module_router)
app.include_router(lesson_router)
app.include_router(progress_router)
app.include_router(assignment_router)
app.include_router(quiz_router)
app.include_router(session_router)
app.include_router(discussion_router)
app.include_router(announcement_router)
app.include_router(notification_router)
app.include_router(audit_router)