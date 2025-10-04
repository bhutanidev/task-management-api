from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.db import get_db
from app.schemas import tasks as schemas
from app.services import tasks as service
from app.services import categories as category_service
from app.routers.auth import get_current_user
from app.models.user import User
from app.models.tasks import TaskStatus, TaskPriority

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def validate_query_params(request: Request):
    """
    Validate that only allowed query parameters are used
    """
    allowed_params = {"status", "priority", "category", "due_from", "due_to"}
    query_params = set(request.query_params.keys())
    
    invalid_params = query_params - allowed_params
    
    if invalid_params:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid query parameter(s): {', '.join(invalid_params)}. Allowed parameters: {', '.join(allowed_params)}"
        )


@router.post("", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: schemas.TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task
    - If no category provided, defaults to "Personal"
    - If category doesn't exist, it will be created
    """
    new_task = await service.create_task(db, task_data, current_user.id)
    
    # Fetch category name for response
    if new_task.category_id:
        category = await category_service.get_category_by_id(db, new_task.category_id)
        task_response = schemas.TaskResponse.model_validate(new_task)
        task_response.category_name = category.name if category else None
        return task_response
    
    return new_task


@router.get("", response_model=List[schemas.TaskResponse], dependencies=[Depends(validate_query_params)])
async def list_tasks(
    status_filter: Optional[TaskStatus] = Query(None, alias="status"),
    priority_filter: Optional[TaskPriority] = Query(None, alias="priority"),
    category_id: Optional[UUID] = Query(None, alias="category"),
    due_date_from: Optional[datetime] = Query(None, alias="due_from"),
    due_date_to: Optional[datetime] = Query(None, alias="due_to"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all tasks for the authenticated user with optional filters
    - status: Filter by task status (pending, in_progress, completed)
    - priority: Filter by task priority (low, medium, high)
    - category: Filter by category ID
    - due_from: Filter tasks with due date >= this value
    - due_to: Filter tasks with due date <= this value
    """
    tasks = await service.get_user_tasks(
        db,
        current_user.id,
        status=status_filter,
        priority=priority_filter,
        category_id=category_id,
        due_date_from=due_date_from,
        due_date_to=due_date_to
    )
    
    # Enrich with category names
    task_responses = []
    for task in tasks:
        task_response = schemas.TaskResponse.model_validate(task)
        if task.category_id:
            category = await category_service.get_category_by_id(db, task.category_id)
            task_response.category_name = category.name if category else None
        task_responses.append(task_response)
    
    return task_responses


@router.get("/{task_id}", response_model=schemas.TaskResponse)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a single task by ID
    """
    task = await service.get_task_by_id(db, task_id, current_user.id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Enrich with category name
    task_response = schemas.TaskResponse.model_validate(task)
    if task.category_id:
        category = await category_service.get_category_by_id(db, task.category_id)
        task_response.category_name = category.name if category else None
    
    return task_response


@router.put("/{task_id}", response_model=schemas.TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: schemas.TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a task
    - Only updates fields that are provided
    - Automatically sets completed_at when status changes to completed
    """
    updated_task = await service.update_task(db, task_id, current_user.id, task_data)
    
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Enrich with category name
    task_response = schemas.TaskResponse.model_validate(updated_task)
    if updated_task.category_id:
        category = await category_service.get_category_by_id(db, updated_task.category_id)
        task_response.category_name = category.name if category else None
    
    return task_response


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a task
    """
    deleted = await service.delete_task(db, task_id, current_user.id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return None