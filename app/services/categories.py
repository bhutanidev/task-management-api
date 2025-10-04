from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID

from app.models.categories import Category
from app.schemas.categories import CategoryCreate, CategoryUpdate


async def get_category_by_name(db: AsyncSession, name: str) -> Optional[Category]:
    """Get category by name (case-insensitive)"""
    result = await db.execute(
        select(Category).where(Category.name.ilike(name))
    )
    return result.scalar_one_or_none()


async def get_category_by_id(db: AsyncSession, category_id: UUID) -> Optional[Category]:
    """Get category by ID"""
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    return result.scalar_one_or_none()


async def get_all_categories(db: AsyncSession) -> List[Category]:
    """Get all categories"""
    result = await db.execute(select(Category).order_by(Category.name))
    return result.scalars().all()


async def create_category(db: AsyncSession, category_data: CategoryCreate) -> Category:
    """Create a new category"""
    new_category = Category(
        name=category_data.name,
        color=category_data.color
    )
    
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    
    return new_category


async def get_or_create_category(db: AsyncSession, category_name: str) -> Category:
    """Get existing category or create new one"""
    # Check if category exists (case-insensitive)
    category = await get_category_by_name(db, category_name)
    
    if category:
        return category
    
    # Create new category
    new_category = Category(name=category_name)
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    
    return new_category


async def ensure_default_category(db: AsyncSession) -> Category:
    """Ensure 'Personal' category exists and return it"""
    return await get_or_create_category(db, "Personal")