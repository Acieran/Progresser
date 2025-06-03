from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

class Entities:
    pass

@dataclass
class Task(Entities):
    user: User
    title: str
    description: str | None = None
    due_date: datetime | None = None
    priority: int | None = None
    is_complete: bool | None = None
    parent_task_id: int | None = None
    weight: int = 1
    children_tasks: list[Task] | None = None

@dataclass
class User(Entities):
    username: str
    active: bool = True
    telegram_username: str | None = None

@dataclass
class TelegramUser(Entities):
    user_id: int
    telegram_username: str
    telegram_state: str | None = None
