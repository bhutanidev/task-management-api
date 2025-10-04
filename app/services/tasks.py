from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.models.tasks import Task, TaskStatus , TaskPriority
from app.schemas.tasks import TaskCreate, TaskUpdate
from app.services.categories import get_or_create_category, ensure_default_category


async def get_task_by_id(db: AsyncSession, task_id: UUID, user_id: UUID) -> Optional[Task]:
    """Get task by ID (only if it belongs to the user)"""
    result = await db.execute(
        select(Task).where(
            and_(Task.id == task_id, Task.user_id == user_id)
        )
    )
    return result.scalar_one_or_none()


async def get_user_tasks(
    db: AsyncSession,
    user_id: UUID,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    category_id: Optional[UUID] = None,
    due_date_from: Optional[datetime] = None,
    due_date_to: Optional[datetime] = None
) -> List[Task]:
    """Get all tasks for a user with optional filters"""
    query = select(Task).where(Task.user_id == user_id)
    
    # Apply filters
    if status:
        query = query.where(Task.status == status)
    
    if priority:
        query = query.where(Task.priority == priority)
    
    if category_id:
        query = query.where(Task.category_id == category_id)
    
    if due_date_from:
        query = query.where(Task.due_date >= due_date_from)
    
    if due_date_to:
        query = query.where(Task.due_date <= due_date_to)
    
    # Order by created_at descending (newest first)
    query = query.order_by(Task.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()
async def create_task(db: AsyncSession, task_data: TaskCreate, user_id: UUID) -> Task:
    """Create a new task"""
    # Handle category
    if task_data.category_name:
        category = await get_or_create_category(db, task_data.category_name)
    else:
        # Default to "Personal" category
        category = await ensure_default_category(db)
    
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        due_date=task_data.due_date,
        user_id=user_id,
        category_id=category.id
    )
    
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    return new_task


async def update_task(
    db: AsyncSession,
    task_id: UUID,
    user_id: UUID,
    task_data: TaskUpdate
) -> Optional[Task]:
    """Update a task"""
    task = await get_task_by_id(db, task_id, user_id)
    
    if not task:
        return None
    
    # Update fields
    update_data = task_data.model_dump(exclude_unset=True)
    
    # Handle category update
    if "category_name" in update_data and update_data["category_name"]:
        category = await get_or_create_category(db, update_data["category_name"])
        task.category_id = category.id
        del update_data["category_name"]
    
    # Handle status change to completed
    if "status" in update_data and update_data["status"] == TaskStatus.COMPLETED:
        if not task.completed_at:
            task.completed_at = datetime.utcnow()
    elif "status" in update_data and update_data["status"] != TaskStatus.COMPLETED:
        # If changing from completed to another status, clear completed_at
        task.completed_at = None
    
    # Update other fields
    for field, value in update_data.items():
        setattr(task, field, value)
    
    await db.commit()
    await db.refresh(task)
    
    return task


async def delete_task(db: AsyncSession, task_id: UUID, user_id: UUID) -> bool:
    """Delete a task"""
    task = await get_task_by_id(db, task_id, user_id)
    
    if not task:
        return False
    
    await db.delete(task)
    await db.commit()
    
    return True