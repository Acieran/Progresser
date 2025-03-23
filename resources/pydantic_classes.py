from enum import Enum

from pydantic import BaseModel, Field

class States(str, Enum):
    none = None
    creating_workspace = "creating workspace"
    creating_task_list = "creating_task_list"
    creating_task = "creating_task"

class BaseObject(BaseModel):
    name: str = Field(...,max_length=100, alias="Имя")
    description: str | None = Field(None, max_length=1000, alias="Описание")
    weight: float = Field(default=1,ge=0,le=100, alias="Вес")

class TaskList(BaseObject):
    workspace_name: str = Field(...,max_length=30, alias="Имя Рабочего пространства")

class Task(BaseObject):
    list_name: str = Field(..., max_length=100, alias="Имя списка")
    completed: bool = Field(default=False, alias="Завершено")