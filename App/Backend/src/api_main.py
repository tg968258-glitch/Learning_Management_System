from fastapi import FastAPI

from Backend.src.routes.student_routes import router as student_router
from Backend.src.routes.course_routes import router as course_router
from Backend.src.routes.enrollment_routes import router as enrollment_router


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