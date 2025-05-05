from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class States(str, Enum):
    none = None
    creating_workspace = "creating workspace"
    creating_task_list = "creating_task_list"
    creating_task = "creating_task"

class BaseObject(BaseModel):
    id: Optional[int] = Field(alias="Id")
    name: str = Field(...,max_length=255, alias="Name")
    description: Optional[str] | None = Field(None, max_length=1000, alias="Description")
    owner_name: [str] = Field(alias="Owner Name")

class Workspace(BaseObject):
    pass

class Task(BaseObject):
    workspace_name: str = Field(..., max_length=255, alias="Workspace Name")
    parent_name: str = Field(None, max_length=255, alias="Parent Name")
    completed: bool = Field(default=False, alias="Completed")
    weight: Optional[float] = Field(default=1, ge=1, le=100, alias="Weight")
