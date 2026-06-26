# routes/uploads.py: File attachment upload routes
import shutil
from fastapi import APIRouter, Depends, File, UploadFile, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_async_session
from app.models import Task, User
from app.schemas import TaskResponse
from app.dependencies import get_active_user
from app.config import settings
from app.exceptions import EntityNotFoundException, AccessDeniedException

router = APIRouter(prefix="/uploads", tags=["File Uploads"])

@router.post(
    "/tasks/{task_id}/attachment",
    response_model=TaskResponse,
    summary="Upload an attachment for a task"
)
async def upload_task_attachment(
    task_id: int = Path(..., gt=0, description="The ID of the task to attach a file to"),
    file: UploadFile = File(..., description="The file attachment (PDF, Image, text, etc.)"),
    current_user: User = Depends(get_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Upload a file and attach its saved path to a specific task.
    Demonstrates:
    - `File` and `UploadFile` parameters.
    - Handling multipart form uploads in FastAPI.
    - Asynchronous chunk reading.
    - Saving files locally using standard filesystem utilities.
    """
    # Verify task existence and ownership
    query = select(Task).where(Task.id == task_id).options(selectinload(Task.category))
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise EntityNotFoundException(f"Task with ID {task_id} not found")
    if task.owner_id != current_user.id:
        raise AccessDeniedException("You do not have permission to attach files to this task")

    # Define path to save file: static directory + task_id prefix to prevent filename collision
    safe_filename = f"task_{task_id}_{file.filename}"
    file_path = settings.UPLOAD_DIR / safe_filename

    # Read uploaded file contents asynchronously and write locally
    # It is recommended to use standard buffered write for large files
    with open(file_path, "wb") as buffer:
        # Read the file in chunks to avoid overloading memory for large files
        while content := await file.read(1024 * 1024):  # 1MB chunks
            buffer.write(content)

    # Save relative path to DB so it can be served or referenced
    relative_path = f"/static/uploads/{safe_filename}"
    task.attachment_path = relative_path
    
    await db.commit()
    await db.refresh(task)
    
    return task
