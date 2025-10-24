from fastapi import APIRouter, Depends
from interfaces.shared.schemas import Task  # Your existing DTOs

# Use your existing use cases through dependency injection
tasks_router = APIRouter(tags=["tasks"])

@tasks_router.get("/tasks")
async def get_tasks():
    # This will call your existing task use cases
    return {"tasks": []}

@tasks_router.get("/tasks/{task_id}")
async def get_task(task_id: int):
    return {"task_id": task_id}

