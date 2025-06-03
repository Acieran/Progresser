from telebot.async_telebot import AsyncTeleBot

from infrastructure.error_handler.errors import CustomError


def handle_error(bot: AsyncTeleBot, chat_id: int, error: CustomError) -> None:
    bot.send_message(chat_id, error.error_message)