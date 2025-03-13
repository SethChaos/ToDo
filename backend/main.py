from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from tortoise.contrib.fastapi import register_tortoise
from tortoise.transactions import in_transaction
from models import Task
from config import TORTOISE_ORM

app = FastAPI()

# Initialize Tortoise ORM
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)

# Global variable to keep track of deleted tasks
deleted = 0

# Pydantic models for request validation
class TaskCreate(BaseModel):
    title: str
    description: str = None

class TaskUpdate(BaseModel):
    title: str = None
    description: str = None
    is_complete: bool = None

# Endpoint: GET unfinished tasks
@app.get("/tasks", response_model=List[TaskCreate])
async def get_tasks():
    tasks = await Task.filter(is_complete=False).all()
    return tasks

# Endpoint: POST create a new task
@app.post("/tasks")
async def create_task(task: TaskCreate):
    new_task = await Task.create(title=task.title, description=task.description)
    return new_task

# Endpoint: PUT update a task
@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task: TaskUpdate):
    existing_task = await Task.filter(id=task_id).first()
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.title is not None:
        existing_task.title = task.title
    if task.description is not None:
        existing_task.description = task.description
    if task.is_complete is not None:
        existing_task.is_complete = task.is_complete
    await existing_task.save()
    return existing_task

# Endpoint: DELETE a single task
@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    global deleted
    task = await Task.filter(id=task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await task.delete()
    deleted += 1
    return {"detail": "Task deleted successfully"}

# Endpoint: DELETE multiple tasks (bulk delete)
@app.delete("/tasks/bulk-delete")
async def bulk_delete_tasks(task_ids: List[int]):
    global deleted
    async with in_transaction() as conn:
        tasks = await Task.filter(id__in=task_ids).using_db(conn).all()
        if not tasks:
            raise HTTPException(status_code=404, detail="No tasks found for the provided IDs")
        await Task.filter(id__in=task_ids).using_db(conn).delete()
        deleted += len(tasks)
    return {"detail": f"{len(tasks)} tasks deleted successfully"}

# Endpoint: GET Dashboard Data
@app.get("/dashboard")
async def get_dashboard():
    total_tasks = await Task.all().count()
    modified_tasks = await Task.filter(updated_at__isnull=False).count()
    deleted_tasks = deleted  
    return {
        "total_tasks": total_tasks,
        "modified_tasks": modified_tasks,
        "deleted_tasks": deleted_tasks,
    }