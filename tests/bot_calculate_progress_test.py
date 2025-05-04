import os

import pytest
from dotenv import load_dotenv

from core.models_sql_alchemy.models import Task
from resources.statics import Statics
from telegram_bot.bot import Bot


@pytest.fixture
def bot():
    """Pytest fixture to create a Bot instance for each test."""
    load_dotenv()
    token = os.getenv('TOKEN')
    Statics.COMPONENTS_PROGRESS.clear()
    return Bot(token)

def test_calculate_progress_already_in_cache(bot):
    # Arrange
    task = Task(id=1, name="Test Task", completed=False, child_tasks=[])
    Statics.COMPONENTS_PROGRESS[(1, Task)] = 50.0  # Pre-populate the cache

    # Act
    progress = bot._calculate_progress(task)

    # Assert
    assert progress == 50.0
    assert len(Statics.COMPONENTS_PROGRESS) == 1  # Cache should not be modified


def test_calculate_progress_no_children_completed_false(bot):
    # Arrange
    task = Task(id=1, name="Test Task", completed=False, child_tasks=[])

    # Act
    progress = bot._calculate_progress(task)

    # Assert
    assert progress == 0.0
    assert Statics.COMPONENTS_PROGRESS[(1,Task)] == 0.0  # Check the cache


def test_calculate_progress_no_children_completed_true(bot):
    # Arrange
    task = Task(id=1, name="Test Task", completed=True, child_tasks=[])

    # Act
    progress = bot._calculate_progress(task)

    # Assert
    assert progress == 100.0
    assert Statics.COMPONENTS_PROGRESS[(1,Task)] == 100.0


def test_calculate_progress_with_children_no_completion(bot):
    # Arrange
    child1 = Task(id=2, name="Child 1", completed=False, weight=1, child_tasks=[])
    child2 = Task(id=3, name="Child 2", completed=False, weight=1, child_tasks=[])
    parent = Task(id=1, name="Parent", completed=False, child_tasks=[child1, child2])

    # Act
    progress = bot._calculate_progress(parent)

    # Assert
    assert progress == 0.0
    assert Statics.COMPONENTS_PROGRESS[(1,Task)] == 0.0
    assert Statics.COMPONENTS_PROGRESS[(2,Task)] == 0.0
    assert Statics.COMPONENTS_PROGRESS[(3,Task)] == 0.0


def test_calculate_progress_with_children_some_completion(bot):
    # Arrange
    child1 = Task(id=2, name="Child 1", completed=True, weight=1, child_tasks=[])
    child2 = Task(id=3, name="Child 2", completed=False, weight=1, child_tasks=[])
    parent = Task(id=1, name="Parent", completed=False, child_tasks=[child1, child2])

    # Act
    progress = bot._calculate_progress(parent)

    # Assert
    assert progress == 50.0
    assert Statics.COMPONENTS_PROGRESS[(1,Task)] == 50.0
    assert Statics.COMPONENTS_PROGRESS[(2,Task)] == 100.0
    assert Statics.COMPONENTS_PROGRESS[(3,Task)] == 0.0


def test_calculate_progress_with_children_all_completion(bot):
    # Arrange
    child1 = Task(id=2, name="Child 1", completed=True, weight=0.5, child_tasks=[])
    child2 = Task(id=3, name="Child 2", completed=True, weight=0.5, child_tasks=[])
    parent = Task(id=1, name="Parent", completed=False, child_tasks=[child1, child2])

    # Act
    progress = bot._calculate_progress(parent)

    # Assert
    assert progress == 100.0
    assert Statics.COMPONENTS_PROGRESS[(1,Task)] == 100.0
    assert Statics.COMPONENTS_PROGRESS[(2,Task)] == 100.0
    assert Statics.COMPONENTS_PROGRESS[(3,Task)] == 100.0


def test_calculate_progress_with_nested_children(bot):
    # Arrange
    grandchild1 = Task(id=4, name="Grandchild 1", completed=True, weight=10, child_tasks=[])
    child1 = Task(id=2, name="Child 1", completed=True, weight=5, child_tasks=[grandchild1])
    child2 = Task(id=3, name="Child 2", completed=False, weight=5, child_tasks=[])
    parent = Task(id=1, name="Parent", completed=False, child_tasks=[child1, child2])

    # Act
    progress = bot._calculate_progress(parent)

    # Assert
    assert progress == 50.0
    assert Statics.COMPONENTS_PROGRESS[(1,Task)] == 50.0
    assert Statics.COMPONENTS_PROGRESS[(2,Task)] == 100.0
    assert Statics.COMPONENTS_PROGRESS[(3,Task)] == 0
    assert Statics.COMPONENTS_PROGRESS[(4,Task)] == 100.0

def test_calculate_progress_with_children_different_weights(bot):
    # Arrange
    child4 = Task(id=5, name="Child 4", completed=True, weight=5, child_tasks=[])
    child3 = Task(id=4, name="Child 3", completed=False, weight=10, child_tasks=[])
    child1 = Task(id=2, name="Child 1", completed=True, weight=20, child_tasks=[])
    child2 = Task(id=3, name="Child 2", completed=False, weight=65, child_tasks=[])
    parent = Task(id=1, name="Parent", completed=False, child_tasks=[child1, child2, child3, child4])

    # Act
    progress = bot._calculate_progress(parent)

    # Assert
    assert progress == 25.0
    # 5 + 0  + 20 + 0 = 25
    # 5 + 10 + 20 + 65 = 100
    assert Statics.COMPONENTS_PROGRESS[(1,Task)] == 25.0
    assert Statics.COMPONENTS_PROGRESS[(2,Task)] == 100.0
    assert Statics.COMPONENTS_PROGRESS[(3,Task)] == 0
    assert Statics.COMPONENTS_PROGRESS[(4,Task)] == 0
    assert Statics.COMPONENTS_PROGRESS[(5,Task)] == 100.0


def test_calculate_progress_with_zero_sum_all(bot):
    # Arrange
    child1 = Task(id=2, name="Child 1", completed=False, weight=0, child_tasks=[])
    child2 = Task(id=3, name="Child 2", completed=False, weight=0, child_tasks=[])
    parent = Task(id=1, name="Parent", completed=False, child_tasks=[child1, child2])

    # Act
    progress = bot._calculate_progress(parent)

    # Assert
    assert progress == 0.0  # Should not raise ZeroDivisionError
    assert Statics.COMPONENTS_PROGRESS[(1,Task)] == 0.0
    assert Statics.COMPONENTS_PROGRESS[(2,Task)] == 0.0
    assert Statics.COMPONENTS_PROGRESS[(3,Task)] == 0.0