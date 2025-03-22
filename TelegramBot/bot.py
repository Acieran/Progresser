import os
import logging
import asyncio

from aiohttp.web_fileresponse import content_type
from sqlalchemy.exc import SQLAlchemyError
from telebot import types

from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot

from DataBase.database_service import DatabaseService
from DataBase.schemas import User, Workspace, UserState

# --- Configuration ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='TelegramBot/bot.log',
    filemode='w',
    encoding='utf-8'
)

class Bot:
    def __init__(self, token):
        self.bot = AsyncTeleBot(token=token)
        self.logger = logging.getLogger(__name__) # Logger for Bot
        self.database = DatabaseService()
        self.handlers = []
        self.register_handlers()

    def handler(self, **kwargs):  # Custom decorator factory
        def decorator(func):
            @self.bot.message_handler(**kwargs)  # Extract register logic to here
            async def wrapper(message):
                return await func(message)  # self here and await
            return wrapper  # Return function for decoration
        return decorator

    def register_handlers(self):
        """Registers handlers that have been decorated"""
        @self.handler(func=lambda message: message.text == 'Новый' or message.text == '/create_user')
        async def create_new_user(message):
            self.log(message)
            chat = message.chat
            try:
                self.database.create_user(chat.username)
                self.logger.info(f"Created new user: {chat.username}")
                await self.bot.reply_to(message,
                                        f"Successfully registered you in the system with username: {chat.username}. \n"
                                        "You can change your username with command /update_username.\n"
                                        "You can use command /view to check your workspaces\n"
                                        "You can use command /create_workspace to create new workspace")
            # TODO Buttons for commands
            except SQLAlchemyError as error:
                self.logger.error(f"Error upon creating user with username - {chat.username}. \n Full message - {message}",
                              exc_info=True)
                await self.bot.reply_to(message, "There was an error with your request")

        @self.handler(commands=['create_workspace'])
        async def create_workspace_handler(message):
            username = message.chat.username
            try:
                self.logger.info(f"User {username} triggered /create_workspace") # log here
                self.set_state(username, "creating workspace")  # Move to the NAME_WORKSPACE state
                await self.bot.send_message(message.chat.id, "What name would you like to give your workspace?")
            except SQLAlchemyError as error:
                self.logger.error(f"Error upon triggering /create_workspace with username - {username}. \n Full message - {message}",
                              exc_info=True)
                await self.bot.send_message(message.chat.id, "There was an error with your request")


        @self.handler(func=lambda message: self.get_state(message.chat.username) == "creating workspace")
        async def process_workspace_name(message):
            chat_id = message.chat.id
            workspace_name = message.text
            username = message.chat.username
            self.logger.info(f"User {username} triggered /create_workspace and entered workspace name - {workspace_name}")
            try:
                self.database.create(Workspace, {"name": workspace_name, "owner_name": username})
                self.logger.info(f"Creating new Workspace for {username} named {workspace_name}")
                await self.bot.send_message(chat_id,
                                            f"Successfully created Workspace named: {workspace_name}.\n"
                                            "You can use command /view to check your workspaces")
            # TODO Buttons for commands
            except SQLAlchemyError as error:
                self.logger.error(
                    f"Error upon creating Workspace for {username} named {workspace_name}. \n Full message - {message}",
                    exc_info=True)
                await self.bot.reply_to(message, "There was an error with your request")
            finally:
                self.clear_state(username)

        @self.handler(commands=['start'])
        async def send_start(message):
            self.log(message)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            print(message)
            username = message.chat.username
            db_user = self.database.get_by_custom_field(User, "telegram_username", username)
            if db_user:
                # context.user_data["user_id"] = db_user.id
                await self.bot.reply_to(message, f"Hello, {db_user.username}, how can I help you? \n"
                                                 "/view to view your workspaces \n"
                                                 "/create_workspace to create new workspace")
            else:
                keyboard.row(
                    types.KeyboardButton('Новый'),
                    types.KeyboardButton('Войти в аккаунт'),
                )
                await self.about(message)
                await self.bot.reply_to(message,
                                        "Seems like, i can't find you in my system, would you like to create an account "
                                        "or you have an existing one?",
                                        reply_markup=keyboard)

        @self.handler(commands=['about'])
        async def send_about(message):
            self.log(message)
            await self.about(message)

        @self.handler()
        async def unprocessed_message(message):
            self.log(self.get_state(message.chat.username))
            self.logger.info(self.get_state(message.chat.username) == "creating workspace")
            self.logger.info(f"There is an unprocessed message: {message.text}\n Full message - {message}")

    def set_state(self, telegram_username, state):
        self.database.update(UserState, telegram_username, {"state": state})

    def get_state(self, telegram_username):
        return self.database.get_by_custom_field(UserState, "telegram_username", telegram_username).state

    def clear_state(self, telegram_username):
        if self.get_state(telegram_username):
            self.database.delete(UserState, telegram_username)


    def log(self, message):
        self.logger.info(message)

    # def register_handlers(self):
    #     """Registers all message handlers."""
    #     self.register_start_handler()
    #     self.register_create_workspace_handler()
    #     self.register_create_new_user()
    #     self.register_about_handler()
    #     # self.register_default_handler()




    def register_process_workspace_handler(self):
        pass




    def about(self, message):
        return self.bot.send_message(message.chat.id, "Hello, im Progressor bot, i'll help to keep track of your progress in any field")



    # @bot.message_handler(content_types=['text'])
    # def context_analyzer(message, context):
    #     if context.user_data["state"] != "create_workspace":
    #         pass
            # try:
            #     user = database.get_by_id()
            #     database.create(Workspace, {'username': chat.username, 'telegram_username': chat.username})
            #     logging.info(f"Created new user: {chat.username}")
            #     await bot.reply_to(message, f"Successfully registered you in the system with username: {chat.username}. "
            #                                 "You can change your username with command /update_username."
            #                                 "You can use command /view to check your workspaces"
            #                                 "You can use command /create_workspace to create new workspace")
            # # TODO Buttons for commands
            # except SQLAlchemyError as error:
            #     logging.error(f"Error upon creating user with username - {chat.username}. \n Full message - {message}",
            #                   exc_info=error)
            #     await bot.reply_to(message, "There was an error with your request")



    async def start_polling(self):
        self.log("Starting bot polling...")
        await self.bot.polling()

async def main():
    load_dotenv()
    token = os.getenv('TOKEN') # Read token

    telegram_bot = Bot(token) # Start bot
    await telegram_bot.start_polling()

if __name__ == '__main__':
    asyncio.run(main())


