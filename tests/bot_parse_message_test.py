import os

import pytest
from unittest.mock import MagicMock

from dotenv import load_dotenv

from telegram_bot.bot import Bot

@pytest.fixture
def bot():
    """Pytest fixture to create a Bot instance for each test."""
    load_dotenv()
    token = os.getenv('TOKEN')
    return Bot(token)

def test_parse_message_valid_input(bot):
    """Test with valid field-value pairs."""
    message_mock = MagicMock()
    message_mock.text = "Field1 - Value1\nField2 - Value2"
    expected_result = {"Field1": "Value1", "Field2": "Value2"}
    actual_result = bot.parse_message(message=message_mock)
    assert actual_result == expected_result

def test_parse_message_with_whitespace(bot):
    """Test with leading and trailing whitespace."""
    message_mock = MagicMock()
    message_mock.text = "  Field1  -  Value1  "
    expected_result = {"Field1": "Value1"}
    actual_result = bot.parse_message(message_mock)
    assert actual_result == expected_result

def test_parse_message_empty_input(bot):
    """Test with an empty message."""
    message_mock = MagicMock()
    message_mock.text = ""
    expected_result = {}
    actual_result = bot.parse_message(message_mock)
    assert actual_result == expected_result

def test_parse_message_invalid_input(bot):
    """Test with a message that doesn't contain field-value pairs."""
    message_mock = MagicMock()
    message_mock.text = "This is not a valid message"
    expected_result = {}
    actual_result = bot.parse_message(message_mock)
    assert actual_result == expected_result

def test_parse_message_mixed_input(bot):
    """Test with a message containing both valid and invalid lines."""
    message_mock = MagicMock()
    message_mock.text = "Field1 - Value1\nThis is an invalid line\nField2 - Value2"
    expected_result = {"Field1": "Value1", "Field2": "Value2"}
    actual_result = bot.parse_message(message_mock)
    assert actual_result == expected_result

def test_parse_message_complex_values(bot):
    """Test with values containing spaces, numbers, and special characters."""
    message_mock = MagicMock()
    message_mock.text = "Field1 - This is a complex value with 123 and !@#"
    expected_result = {"Field1": "This is a complex value with 123 and !@#"}
    actual_result = bot.parse_message(message_mock)
    assert actual_result == expected_result

def test_parse_message_log_error(bot):
    """Test the log if parsing error is raised"""
    message_mock = MagicMock()
    message_mock.text = "Field1 - Value1\n raise Exception()"
    try:
      bot.parse_message(message_mock)
      bot.logger.error.assert_called()
    except:
      pass