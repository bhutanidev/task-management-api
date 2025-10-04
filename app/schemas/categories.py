from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    
    @field_validator('name')
    @classmethod
    def validate_and_lowercase_name(cls, v: str) -> str:
        """
        Validate and normalize category name:
        - Strip whitespace
        - Ensure minimum length
        - Convert to lowercase
        """
        v = v.strip()
        
        if len(v) < 3:
            raise ValueError('Category name must be at least 3 characters long')
        
        return v.lower()


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    
    @field_validator('name')
    @classmethod
    def validate_and_lowercase_name(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate and normalize category name for updates:
        - If None, skip validation (field not being updated)
        - Strip whitespace
        - Ensure minimum length
        - Convert to lowercase
        """
        if v is None:
            return None
        
        v = v.strip()
        
        if len(v) < 3:
            raise ValueError('Category name must be at least 3 characters long')
        
        return v.lower()


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    color: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True