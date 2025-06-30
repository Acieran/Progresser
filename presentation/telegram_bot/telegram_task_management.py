import telebot

from core.application.tasks.task_manager import TaskManager
from core.domain.entities import Task as EntityTask, User as EntityUser
from infrastructure.cache import state_manager
from infrastructure.database.repositories.base_repository import BaseRepository
from infrastructure.database_access_managers.sqlalchemy.models import User as BDUser, Task as BDTask
from infrastructure.error_handler.errors import WrongTransitionError, InternalCreationError, BusinessCreationError
from presentation.telegram_bot.responses.keyboard_markup_manager import reply_markup_dict
from presentation.telegram_bot.responses.telegram_response_manager import automatic_response_generation
from presentation.telegram_bot import state_service
from shared.logging_decorator import log


class TelegramTaskManagement:
    def __init__(self, state_man: state_manager.StateManager, bd_repo: BaseRepository):
        self.task: EntityTask = EntityTask("", "")
        self.state_manager = state_man
        self.bd_repository = bd_repo
        self.type_dict = {
            EntityTask: BDTask,
            EntityUser: BDUser
        }
        self.task_manager = TaskManager(
            db_repository=bd_repo,
            db_model_dict=self.type_dict,
            cache_repo=state_man.user_caching
        )

    @log
    def create_task_handler(self, message):
        split_text = message.text.split()
        command, telegram_username, current_state, next_state = self.get_state_command_username(message)
        user_cache = self.state_manager.get_user_current_task(telegram_username)
        if len(split_text) > 1:
            parent_task_id = split_text[1]
        elif user_cache:
            parent_task_id = user_cache["current_task_id"]
        else:
            parent_task_id = None

        self.switch_to_next_state(telegram_username, next_state)
        self.task = EntityTask(owner_name=telegram_username,parent_task_id=parent_task_id)
        self.state_manager.set_user_current_task(self.task, current_state)
        return self.task

    @log
    def edit_task_handler(self, message):
        split_text = message.text.split()
        command, telegram_username, current_state, next_state = self.get_state_command_username(message)
        if len(split_text) > 1:
            task_id = split_text[1]
        else:
            return ("Команде /edit_task может использоваться только при выборе задачи (/edit_task <Номер задачи>)",
                    reply_markup_dict[current_state])
        self.task = self.task_manager.get_task_use_case(task_id=task_id)
        if not self.task:
            return "Задача с таким Id не найдена", reply_markup_dict[current_state]
        text, reply_markup = automatic_response_generation(
            task_manager=self.task_manager,
            next_state=next_state,
            task=self.task,
        )
        self.switch_to_next_state(telegram_username, next_state)
        return text, reply_markup

    @log
    def user_prompt_based_on_state(self, message: telebot.types.Message):
        task_prompt_state_dict = {
            "task_name_prompt": "title",
            "task_description_prompt": "description",
            "task_due_date_prompt": "due_date",
            "task_priority_prompt": "priority",
            "task_name_prompt_edit": "title",
            "task_description_prompt_edit": "description",
            "task_due_date_prompt_edit": "due_date",
            "task_priority_prompt_edit": "priority",
        }
        input_text, telegram_username, current_state, next_state = self.get_state_command_username(message)
        try:
            if current_state in task_prompt_state_dict.keys():
                self.task.__setattr__(task_prompt_state_dict[current_state], input_text)
            text, reply_markup = automatic_response_generation(
                task_manager=self.task_manager,
                next_state=next_state,
                task=self.task)
        except Exception:
            raise InternalCreationError("Что-то пошло не так", telegram_username, current_state, input_text)
        else:
            self.switch_to_next_state(telegram_username, next_state)
        return text, reply_markup
        
    @staticmethod
    @log
    def check_valid_transition(current_state, command, telegram_username):
        transition_result = state_service.validate_transition(current_state, command)
        if not transition_result["valid"]:
            raise WrongTransitionError(transition_result["error"], telegram_username, current_state, command)
        return transition_result["next_state"]

    @log
    def switch_to_next_state(self, telegram_username, next_state):
        self.state_manager.change_state(telegram_username, next_state)

    @log
    def confirm_creation_handler(self, message):
        return self.confirm_handler(message, self.task_manager.create_new_task_use_case)

    @log
    def confirm_edit_handler(self, message):
        return self.confirm_handler(message, self.task_manager.update_task_use_case)

    @log
    def confirm_deletion_handler(self, message):
        return self.confirm_handler(message, self.task_manager.delete_task_use_case)

    @log
    def get_current_task_set(self, parent_task_id: int | None, telegram_username: str, next_state: str, offset: int = 0):
        tasks = self.task_manager.get_child_tasks_use_case(
            user_id=telegram_username,
            parent_task_id=parent_task_id,
            offset=offset*10,
            limit=10
        )
        if parent_task_id:
            parent_task = self.task_manager.get_task_use_case(
                user_id=telegram_username,
                parent_task_id=parent_task_id
            )
        else:
            parent_task = None
        text, reply_markup = automatic_response_generation(
            task_manager=self.task_manager,
            next_state=next_state,
            task=parent_task,
            child_tasks=tasks)
        return text, reply_markup

    @log
    def confirm_handler(self, message, method):
        command, telegram_username, current_state, next_state = self.get_state_command_username(message)
        if self.task.priority: self.task.priority = int(self.task.priority)
        operation_result = method(
            user_id=telegram_username,
            task_id=self.task.id,
            title=self.task.title,
            description=self.task.description,
            due_date=self.task.due_date,
            priority=self.task.priority,
            parent_task_id=self.task.parent_task_id,
        )
        if operation_result["status"] != "success":
            if operation_result["status"] == "validation_error":
                raise BusinessCreationError(operation_result["errors"], telegram_username, current_state, command)
            raise InternalCreationError(operation_result["errors"], telegram_username, current_state, command)
        else:
            if method == self.task_manager.create_new_task_use_case:
                self.task.id = operation_result["id"]
            self.switch_to_next_state(telegram_username, next_state)
            return self.get_current_task_set(
                parent_task_id=self.task.parent_task_id,
                telegram_username=telegram_username,
                next_state=next_state
            )

    @log
    def cancel_handler(self, message):
        command, telegram_username, current_state, next_state = self.get_state_command_username(message)
        self.switch_to_next_state(telegram_username, next_state)
        return self.get_current_task_set(
                parent_task_id=self.task.parent_task_id,
                telegram_username=telegram_username,
                next_state=next_state
            )

    @log
    def get_current_task_view(self, message):
        telegram_username = message.chat.username
        return self.task_manager.get_child_tasks_use_case(
            user_id=telegram_username,
            parent_task_id=self.task.parent_task_id,
            offset=0,
            limit=10
        )

    @log
    def delete_task_handler(self, message):
        split_text = message.text.split()
        command, telegram_username, current_state, next_state = self.get_state_command_username(message)
        if len(split_text) > 1:
            task_for_deletion = split_text[1]
        else:
            return ("Команде /delete_task может использоваться только при выборе задачи (/delete_task <Номер задачи>)",
                    reply_markup_dict[current_state])
        self.task = self.task_manager.get_task_use_case(
            user_id=telegram_username,
            task_id=task_for_deletion,
        )
        if not self.task:
            return "Задача с таким Id не найдена", reply_markup_dict[current_state]
        text, reply_markup = automatic_response_generation(
            task_manager=self.task_manager,
            next_state=next_state,
            task=self.task,
        )
        self.switch_to_next_state(telegram_username, next_state)
        return text, reply_markup

    @staticmethod
    @log
    def about():
        return "Hello, im Progressor bot, i'll help to keep track of your progress in any field", None

    @log
    def get_state_command_username(self, message):
        command = message.text
        telegram_username = message.chat.username
        current_state = self.state_manager.get_user_state(telegram_username)
        if current_state is None: current_state = "default_short"
        next_state = self.check_valid_transition(current_state, command, telegram_username)
        return command, telegram_username, current_state, next_state