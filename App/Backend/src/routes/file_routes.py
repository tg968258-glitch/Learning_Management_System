from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/files",
    tags=["Files"]
)

UPLOAD_DIR = Path("uploads")


def _get_file_path(file_url: str) -> Path:
    """
    Convert stored URL such as:
    /uploads/resources/sample.pdf

    into local path:
    uploads/resources/sample.pdf
    """

    clean_path = file_url.lstrip("/")

    file_path = Path(clean_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Invalid file path"
        )

    return file_path


@router.get("/view")
def view_file(
    resource_url: str = Query(...)
):
    file_path = _get_file_path(resource_url)

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=file_path.name,
        content_disposition_type="inline"
    )


@router.get("/download")
def download_file(
    resource_url: str = Query(...)
):
    file_path = _get_file_path(resource_url)

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=file_path.name,
        content_disposition_type="attachment"
    )