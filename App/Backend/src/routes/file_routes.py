import mimetypes
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/files",
    tags=["Files"]
)

UPLOAD_DIR = (Path(__file__).resolve().parents[3] / "uploads").resolve()


def _get_file_path(file_url: str) -> Path:
    """
    Convert stored URL such as:
    /uploads/resources/sample.pdf

    into local path:
    uploads/resources/sample.pdf
    """

    clean_path = file_url.split("?", 1)[0].replace("\\", "/").lstrip("/")
    if clean_path.startswith("uploads/"):
        clean_path = clean_path[len("uploads/"):]
    file_path = (UPLOAD_DIR / clean_path).resolve()

    if UPLOAD_DIR not in file_path.parents:
        raise HTTPException(status_code=400, detail="Invalid file path")

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
    resource_url: str | None = Query(None),
    path: str | None = Query(None)
):
    target = resource_url or path
    if not target:
        raise HTTPException(status_code=400, detail="Missing resource_url or path query parameter")
    file_path = _get_file_path(target)

    return FileResponse(
        path=file_path,
        media_type=mimetypes.guess_type(file_path.name)[0] or "application/octet-stream",
        filename=file_path.name,
        content_disposition_type="inline"
    )


@router.get("/download")
def download_file(
    resource_url: str | None = Query(None),
    path: str | None = Query(None)
):
    target = resource_url or path
    if not target:
        raise HTTPException(status_code=400, detail="Missing resource_url or path query parameter")
    file_path = _get_file_path(target)

    return FileResponse(
        path=file_path,
        media_type=mimetypes.guess_type(file_path.name)[0] or "application/octet-stream",
        filename=file_path.name,
        content_disposition_type="attachment"
    )
