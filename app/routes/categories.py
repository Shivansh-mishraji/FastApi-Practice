# routes/categories.py: Category management routes
from typing import List
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import get_async_session
from app.models import Category, User
from app.schemas import CategoryCreate, CategoryResponse
from app.dependencies import get_active_user
from app.exceptions import EntityNotFoundException, AccessDeniedException

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get(
    "/",
    response_model=List[CategoryResponse],
    summary="Get all user categories"
)
async def read_categories(
    current_user: User = Depends(get_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Retrieve all categories created by the authenticated user.
    """
    query = select(Category).where(Category.owner_id == current_user.id)
    result = await db.execute(query)
    categories = result.scalars().all()
    return categories

@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category"
)
async def create_category(
    category_in: CategoryCreate,
    current_user: User = Depends(get_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Create a new category for task categorization (e.g. Work, Personal).
    """
    category = Category(name=category_in.name, owner_id=current_user.id)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category

@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Get a category by ID"
)
async def read_category(
    category_id: int = Path(..., gt=0, description="The ID of the category to retrieve"),
    current_user: User = Depends(get_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Retrieve a specific category by its ID. Users can only view their own categories.
    """
    query = select(Category).where(Category.id == category_id)
    result = await db.execute(query)
    category = result.scalar_one_or_none()

    if not category:
        raise EntityNotFoundException(f"Category with ID {category_id} not found")
    if category.owner_id != current_user.id:
        raise AccessDeniedException("You do not have permission to access this category")
    
    return category

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category"
)
async def delete_category(
    category_id: int = Path(..., gt=0, description="The ID of the category to delete"),
    current_user: User = Depends(get_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Delete a specific category by ID. Cascade constraints will decouple associated tasks.
    """
    query = select(Category).where(Category.id == category_id)
    result = await db.execute(query)
    category = result.scalar_one_or_none()

    if not category:
        raise EntityNotFoundException(f"Category with ID {category_id} not found")
    if category.owner_id != current_user.id:
        raise AccessDeniedException("You do not have permission to delete this category")

    await db.delete(category)
    await db.commit()
    return None
