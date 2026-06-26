# schemas.py: Pydantic models for request and response validation
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

# --- USER SCHEMAS ---

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="The user's email address")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        # Custom validation concept: validate password requirements
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit.")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        return v

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    # Pydantic v2 configuration to enable serialization from SQLAlchemy ORM models
    model_config = ConfigDict(from_attributes=True)


# --- TOKEN SCHEMAS ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None


# --- CATEGORY SCHEMAS ---

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Category name (2-50 characters)")

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)


# --- TASK SCHEMAS ---

class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Task title (3-100 characters)")
    content: str = Field(..., max_length=1000, description="Detailed description of the task")
    status: str = Field(default="pending", description="Task status (pending, in_progress, completed)")
    priority: int = Field(default=1, ge=1, le=5, description="Priority rating from 1 (lowest) to 5 (highest)")
    due_date: Optional[datetime] = Field(default=None, description="Optional due date and time for the task")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_statuses = {"pending", "in_progress", "completed"}
        if v.lower() not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v.lower()

class TaskCreate(TaskBase):
    category_id: Optional[int] = Field(default=None, description="Optional associated category ID")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    priority: Optional[int] = Field(None, ge=1, le=5)
    due_date: Optional[datetime] = Field(None)
    category_id: Optional[int] = Field(None)

    @field_validator("status")
    @classmethod
    def validate_status_update(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid_statuses = {"pending", "in_progress", "completed"}
        if v.lower() not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v.lower()

class TaskResponse(TaskBase):
    id: int
    attachment_path: Optional[str] = None
    owner_id: int
    category_id: Optional[int] = None
    
    # Nested schemas demonstrating relationships
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)
