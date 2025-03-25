import os
import logging
import asyncio
import re
from typing import Optional, Dict, Any, Type

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from telebot import types

from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot

from DataBase.database_service import DatabaseService
from DataBase.schemas import User as BDUser, Workspace as BDWorkspace, UserState as BDUserState, Task as BDTask, \
    TaskList as BDTaskList, Workspace as BDWorkspace
from resources.pydantic_classes import Task
from resources.statics import Messages

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
        self.CLASS_FROM_STATE = {
            # "/create_TaskList": (TaskList, BDTaskList, BDWorkspace),
            "/create_Task": (Task, BDTask, BDWorkspace)
        }
        self.bot = AsyncTeleBot(token=token)
        self.cached_state = {}
        self.logger = logging.getLogger(__name__)  # Logger for Bot
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
            except SQLAlchemyError:
                self.logger.error(
                    f"Error upon creating user with username - {chat.username}. \n Full message - {message}",
                    exc_info=True)
                await self.bot.reply_to(message, "There was an error with your request")

        @self.handler(commands=['create_workspace'])
        async def create_workspace_handler(message):
            username = message.chat.username
            try:
                self.logger.info(f"User {username} triggered /create_workspace")  # log here
                self.set_state(username, "creating workspace")  # Move to the NAME_WORKSPACE state
                await self.bot.send_message(message.chat.id, "What name would you like to give your workspace?")
            except SQLAlchemyError:
                self.logger.error(
                    f"Error upon triggering /create_workspace with username - {username}. \n Full message - {message}",
                    exc_info=True)
                await self.bot.send_message(message.chat.id, "There was an error with your request")

        @self.handler(commands=[list(self.CLASS_FROM_STATE.keys())])
        async def create_something_handler(message):
            await self._create_something_handler(message)

        @self.handler(func=lambda message: self.check_state_and_create(message.chat.username) == "creating workspace")
        async def process_workspace_name(message):
            chat_id = message.chat.id
            workspace_name = message.text
            username = message.chat.username
            self.logger.info(
                f"User {username} triggered /create_workspace and entered workspace name - {workspace_name}")
            try:
                self.database.create(BDWorkspace, {"name": workspace_name, "owner_name": username})
                self.logger.info(f"Creating new Workspace for {username} named {workspace_name}")
                await self.bot.send_message(chat_id,
                                            f"Successfully created Workspace named: {workspace_name}.\n"
                                            "You can use command /view to check your workspaces")
            # TODO Buttons for commands
            except SQLAlchemyError:
                self.logger.error(
                    f"Error upon creating Workspace for {username} named {workspace_name}. \n Full message - {message}",
                    exc_info=True)
                await self.bot.reply_to(message, "There was an error with your request")
            finally:
                self.clear_state(username)

        @self.handler(func=lambda message: self.check_state_and_create(message.chat.username) in list(self.CLASS_FROM_STATE.keys()))
        async def process_something_with_state(message):
            await self._process_something_with_state(message)

        @self.handler(func=lambda message: str(message.text).startswith('/view'))
        async def view_something(message):
            await self._view_something(message)

        @self.handler(commands=['start'])
        async def send_start(message):
            self.log(message)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            print(message)
            username = message.chat.username
            db_user = self.database.get_by_custom_field(BDUser, "telegram_username", username)
            if db_user:
                await self.bot.reply_to(message, f"Hello, {db_user.username}, how can I help you? \n"
                                                 '"/view component name" view your workspaces \n'
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
            self.log(self.check_state_and_create(message.chat.username))
            self.logger.info(self.check_state_and_create(message.chat.username) == "creating workspace")
            self.logger.info(f"There is an unprocessed message: {message.text}\n Full message - {message}")

    # TODO update parse_message, so it can parse message with no explicit fields
    def parse_message(self, message) -> Dict[str, Any]:
        """
        Parses a multi-line message string to extract key-value pairs.

        The message is expected to be in the format "key - value" on separate lines.
        The extracted key-value pairs are stored in a dictionary, which is then returned.
        A boolean dictionary is used to convert string representations of booleans to actual boolean types.

        Args:
            message: A telegram message object containing the text to parse.  Specifically the `message.text` attribute is used.

        Returns:
            A dictionary containing the extracted key-value pairs.  The keys are strings
            extracted from the message, and the values are strings or booleans (if the key
            is "Completed" and the value can be converted to a boolean).  Returns a dictionary.

        Raises:
            KeyError: If the value for 'Completed' is not found in the `boolean_dict`.
            AttributeError: Can be raised by the `re.match` or string operations.

        Example:
            Given a message with the following text:
            "Task - Buy groceries
            Completed - Yes
            Due Date - 2023-12-25"

            The function would return:
            {
                "Task": "Buy groceries",
                "Completed": True,
                "Due Date": "2023-12-25"
            }
        """
        self.logger.info(f"User {message.chat.username} triggered parse_message message - {message.text}")
        text = message.text
        result = {}
        boolean_dict = {
            "Да": True,
            "Нет": False,
            "1": True,
            "0": False,
            "Y": True,
            "N": False,
            "True": True,
            "False": False,
            "Yes": True,
            "No": False,
        }
        try:
            lines = text.splitlines()

            for line in lines:
                match = re.match(r"^(.*?)\s*-\s*(.*)$", line)  # Captures before and after ' - '

                if match:
                    field = match.group(1).strip()
                    value = match.group(2).strip()
                    if field == "Completed":
                        value = boolean_dict[value]
                    result[field] = str(value)
            self.logger.info(f"User {message.chat.username} finished parse_message - successfully")
        except (AttributeError,KeyError) as e:
            self.logger.error(f"Error parsing message - {e}\n Full message - {message}")
            raise e
        finally:
            return result

    def validate_message(self, message, cls: Type) -> Any:
        self.logger.info(f"User {message.chat.username} triggered validate_message for class {cls}")
        try:
            parsed_dict = self.parse_message(message)
        except (AttributeError, KeyError) as e:
            raise e

        try:
            validated_model = cls(**parsed_dict)
            self.logger.info(f"User {message.chat.username} finished validate_message - successfully")
            return validated_model
        except ValidationError as e:
            self.logger.error(f"Error validation message from user {message.chat.username}\n"
                              f"Message - {parsed_dict}\n"
                              f"Error - {e}")
            raise e

    def _process_something_with_state(self, message, send_additional_error_info: bool = False):
        chat_id = message.chat.id
        username = message.chat.username
        try:
            self.logger.info(f"User {username} triggered process_something_with_state")
            state = self.check_state_and_create(message.chat.username)
            cls, bd_cls, bd_cls_parent = self.CLASS_FROM_STATE[state]
            validated_model_dict = self.validate_message(message, cls).__dict__
            parent_record = self.database.get_by_custom_fields(bd_cls_parent,
                                                               owner_name = username,
                                                               name = validated_model_dict["parent_name"]
                                                               )
            if not parent_record:
                send_additional_error_info = True
                raise SQLAlchemyError(f"Parent record with Name {validated_model_dict["parent_name"]} in {bd_cls_parent.__name__} doesn't exist")
            else:
                parent_record = parent_record[0].__dict__
                del validated_model_dict["parent_name"]
                validated_model_dict["parent_id"] = parent_record["id"]
            validated_model_dict["owner_name"] = username
            self.database.create(bd_cls, validated_model_dict)
            self.logger.info(f"User {message.chat.username} finished process_something_with_state - successfully\n"
                             f"created {cls} with fields {validated_model_dict}\n")
            return self.bot.send_message(chat_id,
                                         f"Successfully created {cls.__name__} named: {validated_model_dict["name"]}.\n"
                                         f"You can use command /view_{cls.__name__} to check your {cls.__name__}\n")
        except SQLAlchemyError as e:
            self.logger.error(
                f"Error upon processing message for {username}. \n"
                f"Error - {str(e)}\n"
                f"Full message - {message}",
                exc_info=True)
            error_text = "There was an error with your request"
            if send_additional_error_info: error_text = error_text + f"\n{str(e)}"
            return self.bot.send_message(chat_id, error_text)
        except (ValidationError, AttributeError, KeyError):
            self.logger.error(f"re raising error")
            return self.bot.send_message(chat_id, "There was an error with your request")
        finally:
            self.clear_state(username)

    def set_state(self, telegram_username, state):
        self.check_state_and_create(telegram_username)
        self.database.update(BDUserState, telegram_username, {"state": state})
        self.cached_state[telegram_username] = state

    def check_state_and_create(self, telegram_username):
        try:
            if self.cached_state[telegram_username]:
                return self.cached_state[telegram_username]
        except KeyError:
            self.cached_state[telegram_username] = None
        if not (state := self.database.get_by_id(BDUserState, telegram_username)):
            self.database.create(BDUserState, {"telegram_username": telegram_username, "state": None})
            return None
        else:
            return state

    def clear_state(self, telegram_username):
        if self.database.get_by_id(BDUserState, telegram_username):
            self.database.delete(BDUserState, telegram_username)
        if self.cached_state[telegram_username]:
            del self.cached_state[telegram_username]

    def log(self, message):
        self.logger.info(message)

    def about(self, message):
        return self.bot.send_message(message.chat.id,
                                     "Hello, im Progressor bot, i'll help to keep track of your progress in any field")

    async def _create_something_handler(self, message):
        username = message.chat.username
        try:
            state = message.text
            self.logger.info(f"User {username} triggered {message.text}")
            self.set_state(username, state)
            await self.bot.send_message(message.chat.id, Messages.MESSAGE_FROM_STATE[state])
        except SQLAlchemyError:
            self.logger.error(
                f"Error upon triggering {message.text} with username - {username}. \n Full message - {message}",
                exc_info=True)
            await self.bot.send_message(message.chat.id, "There was an error with your request")

    def _view_something(self, message):
        text = message.text
        username = message.chat.username
        available_classes = {BDWorkspace.__name__: BDWorkspace,
                             BDTask.__name__: BDTask,
                             }
        self.logger.info(f"User {username} triggered process_something_with_state")
        split_text = text.split()
        if len(split_text) != 3:
            return self.bot.send_message(message.chat.id,
                                         "Please specify what you want to view\n"
                                         "Example: /view Workspace Workspace_Name")
        elif split_text[1] not in available_classes.keys():
            return self.bot.send_message(message.chat.id,
                                         "Component not found, please check the spelling"
                                         f"it should be one of {available_classes.keys()}")
        else:
            records = self.database.get_by_custom_fields(available_classes[split_text[1]],
                                               name=split_text[2],
                                               owner_name=username)
            if not records:
                return self.bot.send_message(message.chat.id,
                                             f"Record with name {split_text[2]} in component {split_text[1]} doesn't exist")
            else:
                record = records[0]

    def _calculate_progress(self, record) -> float:
        cls = record.__class__
        cls_parent_mapper = {BDWorkspace: BDTaskList,
                             BDTaskList: BDTask}
        # rows = self.database.get_by_custom_fields(cls,
        #                                        name=split_text[2],
        #                                        owner_name=username)
        # for row in
        # sum_completed = 0
        # sum_all = 0






    async def start_polling(self):
        self.log("Starting bot polling...")
        await self.bot.polling()


async def main():
    load_dotenv()
    token = os.getenv('TOKEN')

    telegram_bot = Bot(token)
    await telegram_bot.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
