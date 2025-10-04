from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.db import get_db
from app.schemas import categories as schemas
from app.services import categories as service
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: schemas.CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new category (authenticated users only)
    """
    # Check if category already exists
    existing_category = await service.get_category_by_name(db, category_data.name)
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category '{category_data.name}' already exists"
        )
    
    new_category = await service.create_category(db, category_data)
    return new_category


@router.get("", response_model=List[schemas.CategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all categories (authenticated users only)
    """
    categories = await service.get_all_categories(db)
    return categories