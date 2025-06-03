from core.application.ports.database import CacheDBConnectionInterface
from core.application.tasks.create_new_task_use_case import create_new_task_use_case
from core.domain.entities import Task as EntityTask, User as EntityUser
from infrastructure.cache import state_manager
from infrastructure.database.repositories.base_repository import BaseRepository
from infrastructure.database_access_managers.sqlalchemy.models import User as BDUser, Task as BDTask
from infrastructure.error_handler.errors import WrongTransitionError, InternalCreationError
from presentation.telegram_bot import state_service


class TelegramTaskCreation:
    def __init__(self, state_man: state_manager.StateManager, bd_repo: BaseRepository):
        self.task = None
        self.state_manager = state_man
        self.bd_repository = bd_repo
        # self.state_manager = state_manager.StateManager(CacheRepositoryUser(redis_connection))
        # self.bd_repository = BaseRepository(SQLDatabaseManager("String"), CachingDatabaseManager())

    def create_task_handler(self, message):
        split_text = message.text.split()
        command = split_text[0]
        telegram_username = message.chat.username
        user_cache = self.state_manager.get_user_cache(telegram_username)
        current_state = user_cache["state"]
        if split_text.length() > 1:
            parent_task_id = split_text[1]
        else:
            parent_task_id = user_cache["current_task_id"] 
        next_state = self.check_valid_transition(current_state, command, telegram_username)
        self.switch_to_next_state(telegram_username, next_state)
        self.task = {
            "user": telegram_username,
            "parent_task": parent_task_id,
            "name": None,
            "description": None,
            "due_date": None,
            "priority": None,
        }

    def user_prompt_based_on_state(self, message):
        task_prompt_state_dict = {
            "task_name_prompt": self.task["name"],
            "task_description_prompt": self.task["description"],
            "task_due_date_prompt": self.task["due_date"],
            "task_priority_prompt": self.task["priority"],
        }
        input_text = message.text
        telegram_username = message.chat.username
        current_state = self.state_manager.get_user_state(telegram_username)
        next_state = self.check_valid_transition(current_state, input_text, telegram_username)
        if current_state in task_prompt_state_dict.keys():
            task_prompt_state_dict[current_state] = input_text
        self.switch_to_next_state(telegram_username, next_state)
        
    def edit_task_handler(self, message):
        command = message.text
        telegram_username = message.chat.username
        current_state = self.state_manager.get_user_state(telegram_username)
        next_state = self.check_valid_transition(current_state, command, telegram_username)
        self.switch_to_next_state(telegram_username, next_state)
        
    @staticmethod
    def check_valid_transition(current_state, command, telegram_username):
        transition_result = state_service.validate_transition(current_state, command)
        if not transition_result["valid"]:
            raise WrongTransitionError(transition_result["error"], telegram_username, current_state, command)
        return transition_result["next_state"]

    def switch_to_next_state(self, telegram_username, next_state):
        self.state_manager.change_state(telegram_username, next_state)

    def confirm_creation_handler(self, message):
        command = message.text
        telegram_username = message.chat.username
        current_state = self.state_manager.get_user_state(telegram_username)
        next_state = self.check_valid_transition(current_state, command, telegram_username)
        type_dict = {
            EntityTask: BDTask,
            EntityUser: BDUser
        }
        operation_result = create_new_task_use_case(
            self.bd_repository,
            type_dict,
            telegram_username,
            self.task["name"],
            self.task["description"],
            self.task["due_date"],
            self.task["priority"],
            self.task["parent_task"],
        )
        if operation_result["statue"] != "success":
            raise InternalCreationError(operation_result["error"], telegram_username, current_state, command)
        else:
            self.switch_to_next_state(telegram_username, next_state)

