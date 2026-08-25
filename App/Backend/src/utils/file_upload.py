import os
import re
from uuid import uuid4
from fastapi import HTTPException, UploadFile, status

# Base uploads directory
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads"))
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB

# Allowed extensions by default (can be customized per use case)
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt", ".zip", ".ppt", ".pptx"}


def sanitize_filename(filename: str) -> str:
    """
    Remove unsafe characters from the filename.
    """
    # Keep alphanumeric, dots, underscores, dashes
    clean = re.sub(r"[^a-zA-Z0-9_.-]", "_", filename)
    return clean.strip("._") or "file"


async def save_uploaded_file(
    file: UploadFile,
    subfolder: str = "assignments",
    allowed_extensions: set[str] = ALLOWED_DOCUMENT_EXTENSIONS,
    max_size: int = MAX_FILE_SIZE_BYTES
) -> str:
    """
    Validates and saves an uploaded file to disk.
    Returns the public URL path (e.g., /uploads/assignments/xxx_filename.pdf).
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a valid filename"
        )

    # Validate file extension
    _, ext = os.path.splitext(file.filename)
    ext_lower = ext.lower()
    if ext_lower not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '{ext}' is not supported. Allowed extensions: {', '.join(sorted(allowed_extensions))}"
        )

    # Ensure target directory exists
    target_dir = os.path.join(UPLOAD_DIR, subfolder)
    os.makedirs(target_dir, exist_ok=True)

    # Generate unique filename
    clean_name = sanitize_filename(file.filename)
    unique_filename = f"{uuid4().hex[:10]}_{clean_name}"
    file_path = os.path.join(target_dir, unique_filename)

    # Stream content to disk and check file size
    size = 0
    try:
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                size += len(chunk)
                if size > max_size:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File size exceeds maximum allowed limit of {max_size // (1024 * 1024)}MB"
                    )
                buffer.write(chunk)
    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {str(e)}"
        )

    # Return URL path accessible via mounted static folder
    return f"/uploads/{subfolder}/{unique_filename}"
