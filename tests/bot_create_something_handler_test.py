import os

import pytest
from unittest.mock import AsyncMock, patch

from dotenv import load_dotenv

from telegram_bot.bot import Bot
from resources.statics import Statics

load_dotenv()
token = os.getenv('TOKEN')
chat_id = os.getenv('CHAT_ID')


@pytest.fixture
def bot_instance():
    bot = Bot(token=token)
    bot.logger = AsyncMock()
    bot.database = AsyncMock()
    bot.cached_state = {}
    return bot

@pytest.fixture
def mock_message():
    # Create a mock Telegram message object
    message = AsyncMock()
    message.chat.id = chat_id
    message.chat.username = "testuser"
    return message

@pytest.mark.asyncio
async def test__create_something_handler_success(bot_instance, mock_message):
    # Test the correct behavior
    mock_message.text = "/create_Task"
    assert correct_class(bot_instance,mock_message.text) == True

    with (
        patch.object(bot_instance, 'set_state', new_callable=AsyncMock) as mock_set_state,
        patch.object(bot_instance.bot, 'send_message', new_callable=AsyncMock) as mock_send_message
    ):

        await bot_instance._create_something_handler(mock_message)

        mock_set_state.assert_called_once_with("testuser", "/create_Task")
        mock_send_message.assert_called_once()

        # Test if method is set correctly and with all parameters that should be present
        args, kwargs = mock_send_message.call_args
        assert args[0] == chat_id
        assert args[1] == Statics.MESSAGE_FROM_STATE["/create_Task"]

# @pytest.mark.asyncio
# async def test__create_something_handler_sql_error(bot_instance, mock_message):
#     # Test code that should have error, that way we know is runs if we do something it does not like
#
#     mock_message.text = "/create_TaskList"
#     assert correct_class(bot_instance,mock_message.text) == True
#
#     with (
#         patch.object(bot_instance, 'set_state', new_callable=AsyncMock) as mock_set_state,
#         patch.object(bot_instance.bot, 'send_message', new_callable=AsyncMock) as mock_send_message
#     ):
#         await bot_instance._create_something_handler(mock_message)
#
#         # Now check the results from above
#         bot_instance.logger.error.assert_called_once()
#         mock_send_message.assert_called_with(chat_id, "There was an error with your request")

@pytest.mark.asyncio
async def test__create_something_handler_invalid_command(bot_instance, mock_message):
    # Setting what is sent
    mock_message.text = "/invalid_command"
    assert correct_class(bot_instance,mock_message.text) == False
    with (
        patch.object(bot_instance.bot, 'send_message', new_callable=AsyncMock) as mock_send_message
    ):
        with pytest.raises(Exception) as e:
            # Run the test by, setting the action
            await bot_instance._create_something_handler(mock_message)

        # Check what is returns and get more code, make sure to be all good for tests
        mock_send_message.assert_not_called()

def correct_class(bot_instance, text: str):
    return text in list(bot_instance.CLASS_FROM_STATE.keys())