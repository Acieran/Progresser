import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telebot import types
from telebot.async_telebot import AsyncTeleBot

from core.application.users.user_manager import UserManager
from infrastructure.database_access_managers.sqlalchemy.models import User as BDUser, Task as BDTask
from core.domain.entities import Task as EntityTask, User as EntityUser
from infrastructure.cache.cache_repository import CacheRepository
from infrastructure.cache.state_manager import StateManager
from infrastructure.database.repositories.base_repository import BaseRepository
from infrastructure.database_access_managers.sqlalchemy.sql_database_manager import SQLDatabaseManager
from infrastructure.database_access_managers.redis.caching_database_manager import CachingDatabaseManager
from presentation.telegram_bot import in_message_handlers
from presentation.telegram_bot.error_handler import CustomErrorHandler
from presentation.telegram_bot.deeplink_start_parser import parse_deep_link
from presentation.telegram_bot.telegram_task_management import TelegramTaskManagement
from shared.logging_decorator import log


class Bot:
    def __init__(self, token):
        # shared_manager.CLASS_FROM_STATE = {
        #     # "/create_TaskList": (TaskList, BDTaskList, BDWorkspace),
        #     "/create_Task": (Task, BDTask, BDWorkspace)
        # }
        # shared_manager.AVAILABLE_CLASSES = {BDWorkspace.__name__: BDWorkspace,
        #                      BDTask.__name__: BDTask,
        #                      }
        self.bot = AsyncTeleBot(token=token)
        self.bot.error_handler = CustomErrorHandler(self.bot)
        self.bot.exception_handler = CustomErrorHandler(self.bot)
        self.exception_handler = self.bot.exception_handler
        self.cached_state = {}
        self.logger = logging.getLogger(__name__)# Logger for Bot
        current_dir = Path(__file__).parent
        db_path = (
                current_dir.parent.parent
                / "infrastructure"
                / "database"
                / "progresser.db"
        ).resolve()
        caching_database_manager = CachingDatabaseManager()
        self.database = BaseRepository(SQLDatabaseManager(f"sqlite:///{db_path}"),caching_database_manager)
        self.handlers = []
        self.register_handlers()
        self.user_manager = UserManager(
            db_repository=self.database,
            db_model_dict={
                EntityTask: BDTask,
                EntityUser: BDUser
            },
            cache_repo=CacheRepository(caching_database_manager)
        )
        self.task_manager = TelegramTaskManagement(StateManager(CacheRepository(caching_database_manager)), self.database)
        self.in_message_handler = in_message_handlers.InMessageHandler(
            bot=self.bot,
            task_manager=self.task_manager,
            exception_handler=self.exception_handler
        )


    @log
    def register_handlers(self):
        """Registers handlers that have been decorated"""
        @self.bot.message_handler(func=lambda message: str(message.text).startswith('/create_task'))
        @log
        async def create_task_message_receiver(message):
            await self.in_message_handler.create_in_message_task_handler(message)

        @self.bot.message_handler(func=lambda message: str(message.text).startswith('/edit_task'))
        @log
        async def edit_task_message_receiver(message):
            await self.in_message_handler.edit_in_message_task_handler(message)

        @self.bot.message_handler(func=lambda message: str(message.text).startswith('/delete_task'))
        @log
        async def delete_task_message_receiver(message):
            await self.in_message_handler.delete_in_message_task_handler(message)

        @self.bot.message_handler(func=lambda message: str(message.text).startswith('/confirm_creation'))
        @log
        async def confirm_task_creation_message_receiver(message):
            try:
                text, reply_markup = self.task_manager.confirm_creation_handler(message)
                await self.bot.reply_to(message, text, reply_markup=reply_markup, parse_mode="MarkdownV2")
            except Exception as e:
                await self.exception_handler.handle_error(e, message.chat.id)

        @self.bot.message_handler(func=lambda message: str(message.text).startswith('/confirm_edit'))
        @log
        async def confirm_task_edit_message_receiver(message):
            try:
                text, reply_markup = self.task_manager.confirm_edit_handler(message)
                await self.bot.reply_to(message=message, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2")
            except Exception as e:
                await self.exception_handler.handle_error(e, message.chat.id)

        @self.bot.message_handler(func=lambda message: str(message.text).startswith('/confirm_deletion'))
        @log
        async def confirm_task_delete_message_receiver(message):
            try:
                text, reply_markup = self.task_manager.confirm_deletion_handler(message)
                await self.bot.reply_to(message=message, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2")
            except Exception as e:
                await self.exception_handler.handle_error(e, message.chat.id)

        @self.bot.message_handler(func=lambda message: str(message.text).startswith('/next'))
        @log
        async def next_message_receiver(message):
            await self.in_message_handler.next_in_message_task_handler(message)


        @self.bot.message_handler(func=lambda message: str(message.text).startswith('/cancel'))
        @log
        async def cancel_message_receiver(message):
            try:
                text, reply_markup = self.task_manager.cancel_handler(message)
                await self.bot.reply_to(message=message, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2")
            except Exception as e:
                await self.exception_handler.handle_error(e, message.chat.id)

        @self.bot.message_handler(commands=['start'])
        @log
        async def send_start(message):
            if len(message.text.split()) > 1:
                parse_deep_link(self.in_message_handler, message)
            else:
                #TODO Redo this part
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                username = message.chat.username
                user = self.user_manager.get_user_or_create_use_case(user_id=username)
                keyboard.row(
                    types.KeyboardButton('/create_task'),
                    types.KeyboardButton('/delete_task'),
                )
                await self.bot.reply_to(message, f"Hello, {user.telegram_username}, how can I help you? \n"
                                                 '"/create_task" to create task \n'
                                                 "/delete_task to delete task", reply_markup=keyboard)

        @self.bot.message_handler(commands=['about'])
        @log
        async def send_about(message):
            text, reply_markup = self.task_manager.about()
            with open("resources/out-0.png", "rb") as photo_file:
                await self.bot.send_photo(
                    chat_id=message.chat.id,
                    photo=photo_file,
                    caption=text,
                    reply_markup=reply_markup
                )

        @self.bot.message_handler()
        @log
        async def handle_any_message(message):
            try:
                text, markup = self.task_manager.user_prompt_based_on_state(message)
                await self.bot.reply_to(message, text, reply_markup=markup)
            except Exception as e:
                await self.exception_handler.handle_error(e = e, chat_id=message.chat.id)

    async def start_polling(self):
        self.logger.info("Starting bot polling...")
        await self.bot.polling()


async def main():
    load_dotenv()
    token = os.getenv('TOKEN')

    telegram_bot = Bot(token)
    await telegram_bot.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
