from enum import Enum

from pydantic import BaseModel, Field

class States(str, Enum):
    none = None
    creating_workspace = "creating workspace"
    creating_task_list = "creating_task_list"
    creating_task = "creating_task"

class BaseObject(BaseModel):
    name: str = Field(...,max_length=100, alias="Name")
    description: str | None = Field(None, max_length=1000, alias="Description")
    weight: float = Field(default=1,ge=0,le=100, alias="Weight")

# class TaskList(BaseObject):
#     parent_name: str = Field(...,max_length=30, alias="Workspace Name")

class Task(BaseObject):
    workspace_name: str = Field(..., max_length=100, alias="Workspace Name")
    parent_name: str = Field(max_length=100, alias="Parent Name")
    completed: bool = Field(default=False, alias="Completed")