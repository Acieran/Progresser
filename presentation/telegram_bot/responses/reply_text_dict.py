text_response_dict = {
    "task_menu": lambda title, description, due_date, priority: (
        f"Task Menu:\n"
        f"Title - {title}\n"
        f"Description - {description}\n"
        f"Due Date - {due_date}\n"
        f"Priority - {priority}\n"
    ),
    "task_menu_edit": lambda title, description, due_date, priority: (
        f"Task Menu:\n"
        f"Title - {title}\n"
        f"Description - {description}\n"
        f"Due Date - {due_date}\n"
        f"Priority - {priority}\n"
    ),
    "task_name_prompt": f"Пожалуйста, напишите имя задачи",
    "task_description_prompt": lambda title, description, due_date, priority: (
        f"Task Menu:\n"
        f"Title - {title}\n"
        f"Description - {description}\n"
        f"Due Date - {due_date}\n"
        f"Priority - {priority}\n"
        f"Пожалуйста, напишите описание задачи"
    ),
    "task_due_date_prompt": lambda title, description, due_date, priority: (
        f"Task Menu:\n"
        f"Title - {title}\n"
        f"Description - {description}\n"
        f"Due Date - {due_date}\n"
        f"Priority - {priority}\n"
        f"Пожалуйста, напишите ожидаемую дату завершения задачи"
    ),
    "task_priority_prompt": lambda title, description, due_date, priority: (
        f"Task Menu:\n"
        f"Title - {title}\n"
        f"Description - {description}\n"
        f"Due Date - {due_date}\n"
        f"Priority - {priority}\n"
        f"Пожалуйста, напишите приоритет задачи"
    ),
    "task_all_prompt": lambda title, description, due_date, priority: (
        f"Task Menu:\n"
        f"Title - {title}\n"
        f"Description - {description}\n"
        f"Due Date - {due_date}\n"
        f"Priority - {priority}\n"
        f"<UNK>, <UNK> <UNK> <UNK>"
    ),
    "task_name_prompt_edit": lambda title, description, due_date, priority: (
        f"Task Menu:\n"
        f"Title - {title}\n"
        f"Description - {description}\n"
        f"Due Date - {due_date}\n"
        f"Priority - {priority}\n"
        f"Пожалуйста, напишите имя задачи"
    ),
    "task_description_prompt_edit": lambda title, description, due_date, priority: (
        f"Task Menu:\n"
        f"Title - {title}\n"
        f"Description - {description}\n"
        f"Due Date - {due_date}\n"
        f"Priority - {priority}\n"
        f"Пожалуйста, напишите описание задачи"
    ),
    "task_due_date_prompt_edit": lambda title, description, due_date, priority: (
        f"Task Menu:\n"
        f"Title - {title}\n"
        f"Description - {description}\n"
        f"Due Date - {due_date}\n"
        f"Priority - {priority}\n"
        f"Пожалуйста, напишите ожидаемую дату завершения задачи"
    ),
    "task_priority_prompt_edit": lambda title, description, due_date, priority: (
        f"Task Menu:\n"
        f"Title - {title}\n"
        f"Description - {description}\n"
        f"Due Date - {due_date}\n"
        f"Priority - {priority}\n"
        f"Пожалуйста, напишите приоритет задачи"
    ),
    "task_all_prompt_edit": lambda title, description, due_date, priority: (
        f"Task Menu:\n"
        f"Title - {title}\n"
        f"Description - {description}\n"
        f"Due Date - {due_date}\n"
        f"Priority - {priority}\n"
        f"<UNK>, <UNK> <UNK> <UNK>"
    ),
    "default_short": lambda title, symbol, progress_bar: (
        f"`{symbol} {title[:50]:<50} {progress_bar}`"
    ),
    "default_detail": lambda title, symbol, progress_bar: (
        f"{symbol} {title[:58]:<58} {progress_bar}"
    ),
    "delete_task_confirmation_prompt": lambda title, description, due_date, priority: (
        f"Вы точно хотите удалить задачу {title}?"
    )
}