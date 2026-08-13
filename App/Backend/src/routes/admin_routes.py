from fastapi import APIRouter

from Backend.src.services.admin_service import get_dashboard_data


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/dashboard")
def admin_dashboard():
    return get_dashboard_data()