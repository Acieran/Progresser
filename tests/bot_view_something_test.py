import os
from unittest.mock import AsyncMock, MagicMock

import pytest
from dotenv import load_dotenv
from telebot import types

from infrastructure.persistance.sqlalchemy.models import Task as BDTask
from infrastructure.persistance.sqlalchemy.models import Workspace as BDWorkspace
from infrastructure.persistance.redis.caching_database_manager import DatabaseService
from resources.statics import Statics
from telegram_bot.bot import Bot


@pytest.fixture
def bot(mocker):
    """Pytest fixture to create a Bot instance for each test."""
    load_dotenv()
    token = os.getenv('TOKEN')
    bot_instance = Bot(token)
    bot_instance.bot = AsyncMock()  # Mock the telebot instance
    bot_instance.database = AsyncMock(spec=DatabaseService)
    mocker.patch.object(bot_instance.bot, "_calculate_progress", new_callable=AsyncMock)
    return bot_instance

@pytest.fixture
def message():
    """Pytest fixture to create a mock message object."""
    msg = AsyncMock(spec=types.Message)
    msg.chat = AsyncMock()
    msg.chat.id = 12345
    msg.chat.username = "testuser"
    return msg


async def test_view_something_invalid_number_of_arguments(bot, message):
    """Test case when the view command has an invalid number of arguments."""
    message.text = "/view Workspace"  # Missing workspace name
    await bot._view_something(message)
    bot.bot.send_message.assert_called_with(message.chat.id,
                                         "Please specify what you want to view\n"
                                         "Example: /view Workspace Workspace_Name")


async def test_view_something_component_not_found(bot, message):
    """Test case when the component specified in the view command is not found."""
    message.text = "/view InvalidComponent WorkspaceName"
    await bot._view_something(message)
    bot.bot.send_message.assert_called_with(message.chat.id,
                                         "Component not found, please check the spelling"
                                         f"it should be one of dict_keys(['Workspace', 'Task'])")


async def test_view_something_record_not_found(bot, message):
    """Test case when the specified record is not found in the database."""
    message.text = "/view Workspace NonExistentWorkspace"
    bot.database.get_by_custom_fields.return_value = []
    await bot._view_something(message)
    bot.bot.send_message.assert_called_with(message.chat.id,
                                             f"Record with name NonExistentWorkspace in component Workspace doesn't exist")



async def test_view_something_success(bot, message):
    """Test case when the view command is successful and a record is found."""
    message.text = "/view Workspace MyWorkspace"
    mock_workspace = MagicMock(spec=BDWorkspace)
    mock_workspace.name = "MyWorkspace"
    mock_workspace.description = "My workspace description"
    mock_workspace.child_tasks = []
    bot.database.get_by_custom_fields.return_value = [mock_workspace]
    bot._calculate_progress = MagicMock(return_value=75.0)

    await bot._view_something(message)

    bot.database.get_by_custom_fields.assert_called_with(BDWorkspace,
                                               name="MyWorkspace",
                                               owner_name="testuser")
    bot._calculate_progress.assert_called_with(mock_workspace)

    expected_message = "[███████░░░] 75.0%\n" \
                       "MyWorkspace\n" \
                       "My workspace description\n"  # Wrap returns a list

    bot.bot.send_message.assert_called_with(message.chat.id, expected_message)

async def test_view_something_with_separate_name_success(bot, message):
    """Test case when the view command is successful and a record is found."""
    message.text = "/view Workspace My Work space"
    mock_workspace = MagicMock(spec=BDWorkspace)
    mock_workspace.name = "My Work space"
    mock_workspace.description = "My workspace description"
    mock_workspace.child_tasks = []
    bot.database.get_by_custom_fields.return_value = [mock_workspace]
    bot._calculate_progress = MagicMock(return_value=75.0)

    await bot._view_something(message)

    bot.database.get_by_custom_fields.assert_called_with(BDWorkspace,
                                               name="My Work space",
                                               owner_name="testuser")
    bot._calculate_progress.assert_called_with(mock_workspace)

    expected_message = "[███████░░░] 75.0%\n" \
                       "My Work space\n" \
                       "My workspace description\n"  # Wrap returns a list

    bot.bot.send_message.assert_called_with(message.chat.id, expected_message)


async def test_view_something_success_with_child_task(bot, message):
    """Test case when the view command is successful and a record is found."""
    message.text = "/view Task MyTask"
    mock_task = MagicMock(spec=BDTask)
    mock_task.name = "MyTask"
    mock_task.description = "My task description"
    mock_task.child_tasks = [BDTask(name="ChildTask1", id=1), BDTask(name="ChildTask2", id=2)]
    Statics.COMPONENTS_PROGRESS[(1,BDTask)] = 50.0
    Statics.COMPONENTS_PROGRESS[(2,BDTask)] = 25.0

    bot.database.get_by_custom_fields.return_value = [mock_task]
    bot._calculate_progress = MagicMock(return_value=75.0)

    await bot._view_something(message)

    bot.database.get_by_custom_fields.assert_called_with(BDTask,
                                               name="MyTask",
                                               owner_name="testuser")
    bot._calculate_progress.assert_called_with(mock_task)

    child1 = f"    {'ChildTask1':<{50}} {'[█████░░░░░] 50.0%'}\n"
    child2 = f"    {'ChildTask2':<{50}} {'[██░░░░░░░░] 25.0%'}\n"
    expected_message = "[███████░░░] 75.0%\n" \
                       "MyTask\n" \
                       "My task description\n"
    expected_message += child1 + child2

    bot.bot.send_message.assert_called_with(message.chat.id, expected_message)

# async def test_view_something_no_child_error(bot, message):
#     """Test case when the view command is successful and a record is found."""
#     message.text = "/view Workspace MyWorkspace"
#     mock_workspace = MagicMock(spec=BDWorkspace)
#     mock_workspace.name = "MyWorkspace"
#     mock_workspace.description = "My workspace description"
#     bot.database.get_by_custom_fields.return_value = [mock_workspace]
#     bot._calculate_progress = MagicMock(return_value=75.0)
#
#     await bot._view_something(message)
#
#     bot.database.get_by_custom_fields.assert_called_with(BDWorkspace,
#                                                name="MyWorkspace",
#                                                owner_name="testuser")
#     bot._calculate_progress.assert_called_with(mock_workspace)
#
#     expected_message = "[███████░░░] 75.0%\n" \
#                        "MyWorkspace\n" \
#                        "My workspace description\n"  # Wrap returns a list
#
#     bot.bot.send_message.assert_called_with(message.chat.id, expected_message)