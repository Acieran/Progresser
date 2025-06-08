from core.application.tasks.create_new_task_use_case import create_new_task_use_case
from core.application.tasks.get_child_tasks_use_case import get_child_tasks_use_case
from core.application.tasks.get_task_use_case import get_task_use_case
from core.domain.entities import Task as EntityTask, User as EntityUser
from infrastructure.cache import state_manager
from infrastructure.database.repositories.base_repository import BaseRepository
from infrastructure.database_access_managers.sqlalchemy.models import User as BDUser, Task as BDTask
from infrastructure.error_handler.errors import WrongTransitionError, InternalCreationError, EntityNotFoundError
from presentation.telegram_bot.telegram_response_manager import TelegramResponseManager, automatic_response_generation
from presentation.telegram_bot import state_service
from shared.logging_decorator import log


class TelegramTaskManagement:
    def __init__(self, state_man: state_manager.StateManager, bd_repo: BaseRepository):
        self.task = None
        self.state_manager = state_man
        self.bd_repository = bd_repo
        self.type_dict = {
            EntityTask: BDTask,
            EntityUser: BDUser
        }
        self.tg_resp_manager = TelegramResponseManager()
        # self.state_manager = state_manager.StateManager(CacheRepositoryUser(redis_connection))
        # self.bd_repository = BaseRepository(SQLDatabaseManager("String"), CachingDatabaseManager())

    @log
    def create_task_handler(self, message):
        split_text = message.text.split()
        command = split_text[0]
        telegram_username = message.chat.username
        user_cache = self.state_manager.get_user_cache(telegram_username)
        parent_task_id = None
        if user_cache:
            current_state = user_cache["state"]
            if split_text.length() > 1:
                parent_task_id = split_text[1]
            else:
                parent_task_id = user_cache["current_task_id"]
        else:
            current_state = "default_short"

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
        return self.task

    @log
    def user_prompt_based_on_state(self, message):
        task_prompt_state_dict = {
            "task_name_prompt": "name",
            "task_description_prompt": "description",
            "task_due_date_prompt": "due_date",
            "task_priority_prompt": "priority",
        }
        input_text = message.text
        telegram_username = message.chat.username
        current_state = "uknown"
        try:
            current_state = self.state_manager.get_user_state(telegram_username)
            next_state = self.check_valid_transition(current_state, input_text, telegram_username)
            if current_state in task_prompt_state_dict.keys():
                self.task[task_prompt_state_dict[current_state]] = input_text
            text, reply_markup = self.tg_resp_manager.create_task_menu_response_handler(next_state, self.task)
        except Exception:
            raise InternalCreationError("Что-то пошло не так", telegram_username, current_state, input_text)
        else:
            self.switch_to_next_state(telegram_username, next_state)
        return text, reply_markup

    @log
    def edit_task_handler(self, message):
        command = message.text
        telegram_username = message.chat.username
        current_state = self.state_manager.get_user_state(telegram_username)
        next_state = self.check_valid_transition(current_state, command, telegram_username)
        text, reply_markup = self.tg_resp_manager.edit_task_data(command, self.task)
        self.switch_to_next_state(telegram_username, next_state)
        return text, reply_markup
        
    @staticmethod
    @log
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
        operation_result = create_new_task_use_case(
            self.bd_repository,
            self.type_dict,
            telegram_username,
            self.task["name"],
            self.task["description"],
            self.task["due_date"],
            self.task["priority"],
            self.task["parent_task"],
        )
        if operation_result["status"] != "success":
            raise InternalCreationError(operation_result["errors"], telegram_username, current_state, command)
        else:
            self.switch_to_next_state(telegram_username, next_state)
            tasks = get_child_tasks_use_case(
                self.bd_repository,
                self.type_dict,
                telegram_username,
                self.task["parent_task"],
            )
            text, reply_markup = automatic_response_generation(next_state, self.task)
            return text, reply_markup

    @log
    def get_current_task_view(self, message):
        telegram_username = message.chat.username
        return get_child_tasks_use_case(self.bd_repository, self.type_dict, telegram_username, self.task["parent_task"])

    @log
    def delete_task_handler(self, message):
        split_text = message.text.split()
        command = split_text[0]
        telegram_username = message.chat.username
        user_cache = self.state_manager.get_user_cache(telegram_username)
        current_state = user_cache["state"]
        if split_text.length() > 1:
            task_for_deletion = split_text[1]
        else:
            task_for_deletion = user_cache["current_task_id"]
        next_state = self.check_valid_transition(current_state, command, telegram_username)
        self.switch_to_next_state(telegram_username, next_state)
        task_dict = get_task_use_case(
            self.bd_repository,
            self.type_dict,
            telegram_username,
            task_for_deletion,
        )
        if task_dict:
            self.switch_to_next_state(telegram_username, next_state)
            return task_dict
        else:
            raise EntityNotFoundError(f"Task with id {task_for_deletion} not found", telegram_username, current_state, command)
