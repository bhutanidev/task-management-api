from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.tasks import TaskStatus, TaskPriority


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM  # Default to MEDIUM
    due_date: Optional[datetime] = None
    category_name: Optional[str] = None
    
    @field_validator('priority', mode='before')
    @classmethod
    def validate_priority(cls, v):
        """
        Handle priority:
        - If None or empty string, default to MEDIUM
        - Otherwise validate as enum
        """
        if v is None or v == "" or (isinstance(v, str) and v.strip() == ""):
            return TaskPriority.MEDIUM
        return v
    
    @field_validator('category_name')
    @classmethod
    def validate_and_default_category(cls, v: Optional[str]) -> str:
        """
        Validate category name:
        - If empty/None, default to 'Personal'
        - If provided, must be at least 3 characters
        - Convert to lowercase
        """
        # Handle None or empty string
        if not v or v.strip() == "":
            return "personal"
        
        # Strip whitespace
        v = v.strip()
        
        # Validate minimum length
        if len(v) < 3:
            raise ValueError('Category name must be at least 3 characters long')
        
        # Convert to lowercase
        return v.lower()


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    category_name: Optional[str] = None
    
    @field_validator('category_name')
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate category name for updates:
        - If None, skip validation (field not being updated)
        - If empty string, default to 'personal'
        - If provided, must be at least 3 characters
        - Convert to lowercase
        """
        # If None, field is not being updated
        if v is None:
            return None
        
        # Handle empty string
        if v.strip() == "":
            return "personal"
        
        # Strip whitespace
        v = v.strip()
        
        # Validate minimum length
        if len(v) < 3:
            raise ValueError('Category name must be at least 3 characters long')
        
        # Convert to lowercase
        return v.lower()


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    category_id: Optional[UUID]
    category_name: Optional[str] = None
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True