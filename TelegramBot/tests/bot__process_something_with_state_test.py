import os

import pytest
from unittest.mock import AsyncMock, MagicMock

from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from telebot.async_telebot import AsyncTeleBot

from DataBase.schemas import TaskList
from TelegramBot.bot import Bot

load_dotenv()
token = os.getenv('TOKEN')
chat_id_dotenv = os.getenv('CHAT_ID')

@pytest.fixture
def bot():
    """Pytest fixture to create a Bot instance."""
    return Bot(token)


def create_message_mock(text, username="test_user", chat_id=chat_id_dotenv):
    """Helper function to create a message mock."""
    message_mock = MagicMock()
    message_mock.text = text
    message_mock.chat.username = username
    message_mock.chat.id = chat_id
    return message_mock


def test_process_tasklist_success(bot, mocker):
    """Test successful processing of a TaskList object."""
    message_text = "Name - My TaskList\nWorkspace Name - My Workspace\nWeight - 50"
    message_mock = create_message_mock(message_text)
    cls = "TaskList"
    name = "My TaskList"
    bot.set_state("test_user", "/create_TaskList")  # Set the state
    mocker.patch.object(bot.bot, "send_message", new_callable=AsyncMock)
    bot._process_something_with_state(message_mock)

    db_record = bot.database.get_by_custom_field(TaskList, "name", "My TaskList") # Assert that DB was called
    assert db_record.name == "My TaskList"
    assert db_record.workspace_name == "My Workspace"
    #check that bot.send message was called.# Real token is optional. Bot object initialization

    bot.bot.send_message.assert_called_once_with(chat_id_dotenv,
                                              f"Successfully created {cls} named: {name}.\n"
                                              f"You can use command /view_{cls} to check your {cls}\n"
                                              )
    assert bot.check_state_and_create("test_user") is None

def test_process_task_success(bot, mocker):
    """Test successful processing of a Task object."""
    message_text = "Name - My Task\nList Name - My TaskList"
    message_mock = create_message_mock(message_text)
    cls = "Task"
    name = "My Task"
    bot.set_state("test_user", "/create_TaskList")  # Set the state
    mocker.patch.object(bot.bot, "send_message", new_callable=AsyncMock)
    bot._process_something_with_state(message_mock)

    db_record = bot.database.get_by_custom_field(TaskList, "name", "My TaskList") # Assert that DB was called
    assert db_record.name == "My TaskList"
    assert db_record.workspace_name == "My Workspace"
    #check that bot.send message was called.# Real token is optional. Bot object initialization

    bot.bot.send_message.assert_called_once_with(chat_id_dotenv,
                                              f"Successfully created {cls} named: {name}.\n"
                                              f"You can use command /view_{cls} to check your {cls}\n"
                                              )
    assert bot.check_state_and_create("test_user") is None

@pytest.mark.asyncio
async def test_process_something_with_state_sqlalchemy_error(bot):
    """Test process something with state raises SQLAlchemyError"""
    message_text = "Имя - My TaskList\nworkspace_name - Test Workspace"
    message_mock = create_message_mock(message_text)
    bot.set_state("test_user", "/create_TaskList")

    # Mock SQLAlchemyError for DB
    bot.database.create.side_effect = SQLAlchemyError()
    bot.bot.send_message = AsyncMock()
    await bot._process_something_with_state(message_mock)

    # Assert send_message was called with some error message
    bot.bot.send_message.assert_called_once()
    assert "There was an error with your request" in str(bot.bot.send_message.call_args)