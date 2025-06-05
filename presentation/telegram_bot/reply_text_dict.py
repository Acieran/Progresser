__task_menu_base = lambda task: (
        f"Task Menu:\n"
        f"Title - {task['name']}\n"
        f"Description - {task['description']}\n"
        f"Due Date - {task['due_date']}\n"
        f"Priority - {task['priority']}\n"
)

text_response_dict = {
    "task_menu": __task_menu_base,
    "task_name_prompt": f"Пожалуйста, напишите имя задачи",
    "task_description_prompt": (
        f"{__task_menu_base}"
        f"Пожалуйста, напишите описание задачи"
    ),
    "task_due_date_prompt": (
        f"{__task_menu_base}"
        f"Пожалуйста, напишите ожидаемую дату завершения задачи"
    ),
    "task_priority_prompt": (
        f"{__task_menu_base}"
        f"Пожалуйста, напишите приоритет задачи"
    ),
    "task_all_prompt": (
        f"{__task_menu_base}"
        f"<UNK>, <UNK> <UNK> <UNK>"
    ),
    "default_short": lambda task, symbol: (
        f"{symbol}{task['name'][:80]:<80} {task['progress_bar']}"
    ),
    "default_detail": lambda task, symbol, progress_bar: (
        f"{symbol}{task['name'][:80]:<80} {progress_bar}"
    # TODO better detail view
    )
}
