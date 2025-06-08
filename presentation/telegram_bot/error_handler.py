import inspect

from telebot.async_telebot import ExceptionHandler

from infrastructure.error_handler.errors import CustomError
from shared.logging_decorator import log, log_exception


class CustomErrorHandler(ExceptionHandler):
    def __init__(self, bot):
        self.bot = bot

    @log
    def handle(self, exception: CustomError) -> bool:
        raise exception

    async def handle_error(self, e, chat_id: int):
        # Get caller's frame (function_0)
        caller_frame = inspect.currentframe().f_back

        # Extract caller function object
        caller_function = caller_frame.f_code.co_name

        log_exception(e, caller_function)
        await self.bot.send_message(chat_id=chat_id, text="There was an error while handling this request.")
