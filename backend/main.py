from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from models import Task
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Initialize the DB (for development)
init_db()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
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
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.is_complete == False).all()
    return tasks

# Endpoint: POST create a new task
@app.post("/tasks")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(title=task.title, description=task.description)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# Endpoint: PUT update a task
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    existing_task = db.query(Task).filter(Task.id == task_id).first()
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.title is not None:
        existing_task.title = task.title
    if task.description is not None:
        existing_task.description = task.description
    if task.is_complete is not None:
        existing_task.is_complete = task.is_complete
    db.commit()
    db.refresh(existing_task)
    return existing_task

# Endpoint: DELETE a single task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    global deleted
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    deleted = deleted + 1
    return {"detail": "Task deleted successfully"}

# Endpoint: DELETE multiple tasks (bulk delete)
@app.delete("/tasks/bulk-delete")
def bulk_delete_tasks(task_ids: List[int], db: Session = Depends(get_db)):
    global deleted
    tasks = db.query(Task).filter(Task.id.in_(task_ids)).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found for the provided IDs")
    for task in tasks:
        db.delete(task)
    db.commit()
    deleted = deleted + len(tasks)
    return {"detail": f"{len(tasks)} tasks deleted successfully"}

# Endpoint: GET Dashboard Data
@app.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    total_tasks = db.query(Task).count()
    modified_tasks = db.query(Task).filter(Task.updated_at != None).count()
    deleted_tasks = deleted  
    return {
        "total_tasks": total_tasks,
        "modified_tasks": modified_tasks,
        "deleted_tasks": deleted_tasks,
    }