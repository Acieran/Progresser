from presentation.telegram_bot.telegram_task_management import TelegramTaskManagement
from shared.logging_decorator import log


class InMessageHandler:
    def __init__(self, bot, task_manager: TelegramTaskManagement, exception_handler):
        self.bot = bot
        self.task_manager = task_manager
        self.exception_handler = exception_handler

    @log
    async def create_in_message_task_handler(self, message):
        try:
            self.task_manager.create_task_handler(message)
            await self.bot.send_message(message.chat.id, "Пожалуйста, введите наименование задачи")
        except Exception as e:
            await self.exception_handler.handle_error(e, message.chat.id)

    @log
    async def edit_in_message_task_handler(self, message):
        try:
            text, markup = self.task_manager.edit_task_handler(message)
            await self.bot.reply_to(message, text, reply_markup=markup)
        except Exception as e:
            await self.exception_handler.handle_error(e, message.chat.id)

    @log
    async def delete_in_message_task_handler(self, message):
        try:
            text, markup = self.task_manager.delete_task_handler(message)
            await self.bot.reply_to(message, text, reply_markup=markup)
        except Exception as e:
            await self.exception_handler.handle_error(e, message.chat.id)

    @log
    async def next_in_message_handler(self, message):
        try:
            text, markup = self.task_manager.delete_task_handler(message)
            await self.bot.reply_to(message, text, reply_markup=markup)
        except Exception as e:
            await self.exception_handler.handle_error(e, message.chat.id)
