from telebot import types

from core.application.tasks.task_manager import TaskManager
from core.domain.entities import Task
from presentation.telegram_bot.responses.generate_short_response import generate_short_response
from presentation.telegram_bot.responses.reply_text_dict import text_response_dict
from presentation.telegram_bot.responses.keyboard_markup_manager import reply_markup_dict
from presentation.telegram_bot.responses.progress_visualiser import get_progress_bar
from shared.logging_decorator import log

ADVANCED_GENERATION = {
    "default_detail",
    "default_short"
}

@log
def automatic_response_generation(
        task_manager: TaskManager,
        next_state: str,
        task: Task | None = None,
        child_tasks: list[Task] = None,
        offset: int = 0
) -> (str, types.ReplyKeyboardMarkup | None):
    if next_state in ADVANCED_GENERATION:
        symbol = ""
        text = ""
        if task:
            progress = task_manager.calculate_progress(task_id=task.id)
            progress_bar = get_progress_bar(progress)
            text = generate_short_response(title = task.title, symbol= symbol, progress_bar=progress_bar, task_id=task.id)
            symbol += "⊢"
        if child_tasks:
            for i, child_task in enumerate(child_tasks):
                if i < 10:
                    progress = task_manager.calculate_progress(task_id=child_task.id)
                    progress_bar = get_progress_bar(progress)
                    text += "\n" + generate_short_response(
                        title = child_task.title,
                        symbol= symbol,
                        progress_bar=progress_bar,
                        task_id=child_task.id
                    )
                else: break
        return text, reply_markup_dict[next_state]
    else:
        return (text_response_dict[next_state](
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            priority=task.priority,
        ), reply_markup_dict[next_state])
