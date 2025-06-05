from telebot import types

from presentation.telegram_bot.reply_text_dict import text_response_dict
from presentation.telegram_bot.keyboard_markup_manager import reply_markup_dict
from shared.logging_decorator import log

ADVANCED_GENERATION = {
    "default_detail",
    "default_short"
}

@log
def automatic_response_generation(
        next_state: str,
        task: dict[str, ...],
        child_tasks: list[dict[str, ...]] = None,
) -> (str, types.ReplyKeyboardMarkup | None):
    if next_state in ADVANCED_GENERATION:
        text = text_response_dict[next_state](task = task, symbol= "")
        for child_task in child_tasks:
            text += "\n" + text_response_dict[child_task](task = child_task, symbol= "⊢")
        return text, reply_markup_dict[next_state]
    else:
        return text_response_dict[next_state](task), reply_markup_dict[next_state]

class TelegramResponseManager:

    @staticmethod
    def create_task_menu_response_handler(next_state: str, task: dict):
        text = (f"Task Menu:"
                f"\nTitle - {task['name']}"
                f"\nDescription - {task['description']}"
                f"\nDue Date - {task['due_date']}"
                f"\nPriority - {task['priority']}"
        )
        keyboard = reply_markup_dict[next_state]

        return text, keyboard

    @staticmethod
    def edit_task_data(next_state: str, command: str, task: dict):
        task_prompt_text_dict = {
            "/edit_name": "Пожалуйста, напишите имя задачи",
            "/edit_description": "Пожалуйста, напишите описание задачи",
            "/edit_due_date": "Пожалуйста, напишите ожидаемую дату задачи",
            "/edit_priority": "Пожалуйста, напишите приоритет задачи",
        }
        text = (f"Task Menu:"
                f"\nTitle - {task['name']}"
                f"\nDescription - {task['description']}"
                f"\nDue Date - {task['due_date']}"
                f"\nPriority - {task['priority']}")
        if command in task_prompt_text_dict.keys():
            text += f"\n{task_prompt_text_dict[command]}"
        keyboard = reply_markup_dict[next_state]
        return text, keyboard
