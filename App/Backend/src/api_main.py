from fastapi import FastAPI

from Backend.src.routes.admin_routes import router as admin_router
from Backend.src.routes.assignment_routes import router as assignment_router
from Backend.src.routes.auth_routes import router as auth_router
from Backend.src.routes.course_routes import router as course_router
from Backend.src.routes.enrollment_routes import router as enrollment_router
from Backend.src.routes.student_routes import router as student_router
from Backend.src.routes.teacher_routes import router as teacher_router

app = FastAPI(
    title="LMS API",
    description="Learning Management System REST API",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "LMS API is running"
    }


app.include_router(student_router)
app.include_router(course_router)
app.include_router(enrollment_router)
app.include_router(teacher_router)
app.include_router(assignment_router)
app.include_router(admin_router)
app.include_router(auth_router)