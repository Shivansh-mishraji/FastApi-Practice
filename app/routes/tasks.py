# routes/tasks.py: Task management routes
from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_async_session
from app.models import Task, Category, User
from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.dependencies import get_active_user
from app.exceptions import EntityNotFoundException, AccessDeniedException

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get(
    "/",
    response_model=List[TaskResponse],
    summary="Get user tasks with filters & pagination"
)
async def read_tasks(
    status_filter: Optional[str] = Query(
        None, 
        alias="status", 
        description="Filter tasks by status (pending, in_progress, completed)"
    ),
    priority_filter: Optional[int] = Query(
        None, 
        alias="priority", 
        ge=1, 
        le=5, 
        description="Filter tasks by priority (1 to 5)"
    ),
    limit: int = Query(10, ge=1, le=100, description="Pagination limit"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Retrieve tasks for the logged-in user.
    Demonstrates:
    - Query parameter validations (`Query`, `ge`, `le`).
    - Pagination offsets and limits.
    - Eager loading of categories (`selectinload`) to prevent N+1 query problems.
    """
    query = select(Task).where(Task.owner_id == current_user.id)

    # Apply filters dynamically
    if status_filter:
        query = query.where(Task.status == status_filter.lower())
    if priority_filter:
        query = query.where(Task.priority == priority_filter)

    # Offset & Limit pagination + preloading category relationship
    query = query.offset(offset).limit(limit).options(selectinload(Task.category))
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks

@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task"
)
async def create_task(
    task_in: TaskCreate,
    current_user: User = Depends(get_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Create a new task. If category_id is provided, validates ownership of the category.
    """
    if task_in.category_id:
        # Validate that category exists and belongs to this user
        cat_query = select(Category).where(
            Category.id == task_in.category_id, 
            Category.owner_id == current_user.id
        )
        cat_result = await db.execute(cat_query)
        if not cat_result.scalar_one_or_none():
            raise EntityNotFoundException(f"Category with ID {task_in.category_id} not found or access denied")

    new_task = Task(
        title=task_in.title,
        content=task_in.content,
        status=task_in.status,
        priority=task_in.priority,
        due_date=task_in.due_date,
        category_id=task_in.category_id,
        owner_id=current_user.id
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    # Refresh task with preloaded category relationship for response schema mapping
    query = select(Task).where(Task.id == new_task.id).options(selectinload(Task.category))
    result = await db.execute(query)
    return result.scalar_one()

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a task by ID"
)
async def read_task(
    task_id: int = Path(..., gt=0, description="The ID of the task to retrieve"),
    current_user: User = Depends(get_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Retrieve a specific task by ID. Ensures current user ownership.
    """
    query = select(Task).where(Task.id == task_id).options(selectinload(Task.category))
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise EntityNotFoundException(f"Task with ID {task_id} not found")
    if task.owner_id != current_user.id:
        raise AccessDeniedException("You do not have permission to view this task")

    return task

@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task"
)
async def update_task(
    task_in: TaskUpdate,
    task_id: int = Path(..., gt=0, description="The ID of the task to update"),
    current_user: User = Depends(get_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Update a task. Allows partial updates.
    """
    query = select(Task).where(Task.id == task_id).options(selectinload(Task.category))
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise EntityNotFoundException(f"Task with ID {task_id} not found")
    if task.owner_id != current_user.id:
        raise AccessDeniedException("You do not have permission to update this task")

    # If category is updating, validate it
    if task_in.category_id is not None:
        cat_query = select(Category).where(
            Category.id == task_in.category_id, 
            Category.owner_id == current_user.id
        )
        cat_result = await db.execute(cat_query)
        if not cat_result.scalar_one_or_none():
            raise EntityNotFoundException(f"Category with ID {task_in.category_id} not found or access denied")

    # Update only the fields that were provided
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task"
)
async def delete_task(
    task_id: int = Path(..., gt=0, description="The ID of the task to delete"),
    current_user: User = Depends(get_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Delete a specific task.
    """
    query = select(Task).where(Task.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise EntityNotFoundException(f"Task with ID {task_id} not found")
    if task.owner_id != current_user.id:
        raise AccessDeniedException("You do not have permission to delete this task")

    await db.delete(task)
    await db.commit()
    return None
