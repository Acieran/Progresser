import os

import pytest
from unittest.mock import AsyncMock, MagicMock

from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from telebot.async_telebot import AsyncTeleBot

from DataBase.schemas import TaskList, Task, Workspace, User
from TelegramBot.bot import Bot

load_dotenv()
token = os.getenv('TOKEN')
chat_id_dotenv = os.getenv('CHAT_ID')

@pytest.fixture
def bot(mocker):
    """Pytest fixture to create a Bot instance."""
    bot_instance = Bot(token)
    bot_instance.database.create_user("test_user")
    mocker.patch.object(bot_instance.bot, "send_message", new_callable=AsyncMock)

    yield bot_instance  # Use yield to allow cleanup after tests

    # Teardown/Cleanup code:
    bot_instance.database.delete(User,"test_user")


def create_message_mock(text, username="test_user", chat_id=chat_id_dotenv):
    """Helper function to create a message mock."""
    message_mock = MagicMock()
    message_mock.text = text
    message_mock.chat.username = username
    message_mock.chat.id = chat_id
    return message_mock


def test_process_tasklist_success(bot):
    """Test successful processing of a TaskList object."""
    cls = TaskList
    name = "My TaskList"
    parent_name = "My Workspace"
    username = "test_user"
    message_text = f"Name - {name}\nWorkspace Name - {parent_name}\nWeight - 50"
    message_mock = create_message_mock(message_text)

    bot.database.create(Workspace, {"name": parent_name, "owner_name": username})
    bot.set_state(username, "/create_TaskList")  # Set the state

    bot._process_something_with_state(message_mock)

    db_record = bot.database.get_by_custom_field(cls, "name", name) # Assert that DB was called
    assert db_record.name == name
    assert db_record.parent_id is not None
    #check that bot.send message was called.# Real token is optional. Bot object initialization

    bot.bot.send_message.assert_called_once_with(chat_id_dotenv,
                                              f"Successfully created {cls.__name__} named: {name}.\n"
                                              f"You can use command /view_{cls.__name__} to check your {cls.__name__}\n"
                                              )
    assert bot.check_state_and_create("test_user") is None

def test_process_task_success(bot):
    """Test successful processing of a Task object."""
    cls = Task
    name = "My Task"
    parent_workspace = "My Workspace"
    parent_name = "My TaskList"
    username = "test_user"
    message_text = f"Name - {name}\nList Name - {parent_name}"
    message_mock = create_message_mock(message_text)

    bot.database.create(Workspace, {"name": parent_workspace, "owner_name": username})
    workspace_record = bot.database.get_by_custom_field(Workspace, "name", parent_workspace)
    bot.database.create(TaskList, {"name": parent_name, "owner_name": username, "parent_id": workspace_record.id})
    bot.set_state("test_user", "/create_Task")  # Set the state

    bot._process_something_with_state(message_mock)

    db_record = bot.database.get_by_custom_field(cls, "name", name) # Assert that DB was called

    assert db_record.name == name
    assert db_record.parent_id is not None

    bot.bot.send_message.assert_called_once_with(chat_id_dotenv,
                                              f"Successfully created {cls.__name__} named: {name}.\n"
                                              f"You can use command /view_{cls.__name__} to check your {cls.__name__}\n"
                                              )
    assert bot.check_state_and_create("test_user") is None

def test_process_tasklist_error_no_parent(bot):
    """Test errorful processing of a TaskList object if no parent exists"""
    cls = TaskList
    bd_cls_parent = Workspace
    name = "My TaskList"
    parent_name = "My Workspace"
    username = "test_user"
    message_text = f"Name - {name}\nWorkspace Name - {parent_name}\nWeight - 50"
    message_mock = create_message_mock(message_text)

    bot.set_state(username, "/create_TaskList")  # Set the state


    bot._process_something_with_state(message_mock)

    db_record = bot.database.get_by_custom_field(cls, "name", name) # Assert that DB was called
    assert db_record is None

    bot.bot.send_message.assert_called_once_with(chat_id_dotenv,
                                              f"There was an error with your request\n"
                                              f"Parent record with Name {parent_name} in {bd_cls_parent.__name__} doesn't exist"
                                              )
    assert bot.check_state_and_create("test_user") is None

def test_process_task_error_no_parent(bot):
    """Test errorful processing of a Task object if no parent exists."""
    cls = Task
    name = "My Task"
    bd_cls_parent = TaskList
    parent_name = "My TaskList"
    username = "test_user"
    message_text = f"Name - {name}\nList Name - {parent_name}"
    message_mock = create_message_mock(message_text)

    bot.set_state(username, "/create_Task")  # Set the state

    bot._process_something_with_state(message_mock)

    db_record = bot.database.get_by_custom_field(cls, "name", name) # Assert that DB was called

    assert db_record is None

    bot.bot.send_message.assert_called_once_with(chat_id_dotenv,
                                                 f"There was an error with your request\n"
                                                 f"Parent record with Name {parent_name} in {bd_cls_parent.__name__} doesn't exist"
                                                 )
    assert bot.check_state_and_create("test_user") is None