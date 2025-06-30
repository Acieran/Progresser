from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

class Entities:
    pass

@dataclass
class Task(Entities):
    owner_name: str
    title: str = None
    id: int = None
    description: str = None
    due_date: datetime = None
    priority: int = None
    is_complete: bool = None
    parent_task_id: int = None
    weight: int = 1
    children_tasks: list[Task] = None

@dataclass
class User(Entities):
    username: str
    active: bool = True
    telegram_username: str = None

@dataclass
class TelegramUser(Entities):
    user_id: int
    telegram_username: str
    telegram_state: str = None
