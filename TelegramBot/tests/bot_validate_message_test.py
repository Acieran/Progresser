import os

import pytest
from unittest.mock import MagicMock

from dotenv import load_dotenv
from pydantic import ValidationError

from resources.pydantic_classes import TaskList, Task
from TelegramBot.bot import Bot

@pytest.fixture
def bot():
    """Pytest fixture to create a Bot instance."""
    load_dotenv()
    token = os.getenv('TOKEN')
    return Bot(token)

def create_message_mock(text, username="test_user", chat_id=123):
    """Helper function to create a message mock."""
    message_mock = MagicMock()
    message_mock.text = text
    message_mock.chat.username = username
    message_mock.chat.id = chat_id
    return message_mock

def test_validate_tasklist_success(bot):
    """Test successful validation of a TaskList object."""
    message_text = "Имя - My TaskList\nИмя Рабочего пространства - My Workspace\nВес - 50"
    message_mock = create_message_mock(message_text)
    tasklist = bot.validate_message(message_mock, TaskList)
    assert isinstance(tasklist, TaskList)
    assert tasklist.name == "My TaskList"
    assert tasklist.workspace_name == "My Workspace"
    assert tasklist.weight == 50.0 # Test Weight

def test_validate_task_invalid_weight(bot):
    """Test validation failure due to an invalid weight value."""
    message_text = "Имя - My Task\nlist_name - 123\nВес - 150"  # Weight > 100
    message_mock = create_message_mock(message_text)

    with bot.validate_message(message_mock, Task) as excinfo: # Expect ValidationError to be raised
        assert excinfo.__class__ == ValidationError
        assert "100" in str(excinfo.value) # Check weight constraint mentioned

def test_validate_message_parse_error(bot):
    """Test when parse_message returns an error."""
    message_text = "Invalid message format"
    message_mock = create_message_mock(message_text)
    bot.parse_message = MagicMock(return_value={"error": ValueError("Parsing error")})

    with pytest.raises(ValueError, match="Parsing error"):
        bot.validate_message(message_mock, TaskList)

def test_baseobject_name_too_long(bot):
    """Test validation failure due to name exceeding max length."""
    message_text = "Имя - " + "A" * 31 + "\nОписание - This is description\nworkspace_name - Test Workspace"  # Name too long
    message_mock = create_message_mock(message_text)

    with pytest.raises(ValidationError) as excinfo:
        bot.validate_message(message_mock, TaskList)

    assert "Имя" in str(excinfo.value)  # check the errors contain the string "Имя"
    assert "string" in str(excinfo.value) #check type of exception

def test_task_valid_completed_false(bot):
    """Test successful validation of Task with completed set to False."""
    message_text = "Имя - My Task\nИмя списка - 123\nЗавершено - Нет"
    message_mock = create_message_mock(message_text)
    task = bot.validate_message(message_mock, Task)
    assert isinstance(task, Task)
    assert task.completed is False # Check completed bool

def test_task_valid_completed_true(bot):
    """Test successful validation of Task with completed set to True."""
    message_text = "Имя - My Task\nИмя списка - 123\nЗавершено - Да"
    message_mock = create_message_mock(message_text)
    task = bot.validate_message(message_mock, Task)
    assert isinstance(task, Task)
    assert task.completed is True # Check completed bool