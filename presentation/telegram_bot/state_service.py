from presentation.telegram_bot import telegram_task_creation

STATES = {"default_short",
          "default_detail",
          "task_name_prompt",
          "task_menu",
          "task_description_prompt",
          "task_priority_prompt",
          "task_due_date_prompt",
          "task_all_prompt",
          "delete_task_confirmation_prompt"
          }

state_transitions = {
    # === Основное меню ===
    "default_short": {
        "/create_task": "task_name_prompt",
        "/create_sub_task": "task_name_prompt",
        "/edit_task": "task_menu",
        "/edit_task <task_id>": {
            "next_state": "task_menu",
            "condition": "task_id exists and accessible"
        },
        "/delete_task": "delete_task_confirmation_prompt",
        "/delete_task <task_id>": {
            "next_state": "delete_task_confirmation_prompt",
            "condition": "task_id exists and accessible"
        },
        "/show_image": "default_short",  # Остаемся в том же состоянии
        "/enter <task_id>": {
            "next_state": "default_short",
            "actions": ["set_current_task(task_id)", "update_breadcrumbs()"]
        },
        "/back": {
            "next_state": "default_short",
            "condition": "breadcrumbs not empty",
            "actions": ["move_to_parent_task()"]
        },
        "/home": {
            "next_state": "default_short",
            "actions": ["reset_to_root()"]
        },
        "/detail": "default_detail",
        "/next": "default_short",  # Пагинация без смены состояния
        "/previous": "default_short"  # Пагинация без смены состояния
    },

    # === Меню задачи ===
    "task_menu": {
        "/edit_name": "task_name_prompt",
        "/edit_description": "task_description_prompt",
        "/edit_due_data": "task_due_date_prompt",
        "/edit_priority": "task_priority_prompt",
        "/edit_all": "task_all_prompt",
        "/confirm_creation": "default_short",
        "/cancel": "default_short"
    },

    # === Поля ввода ===
    "task_name_prompt": {
        "text_input": {
            "next_state": "task_menu",
            "actions": ["update_task_name(text)"]
        },
        "/cancel": "task_menu"
    },
    "task_description_prompt": {
        "text_input": {
            "next_state": "task_menu",
            "actions": ["update_task_description(text)"]
        },
        "/cancel": "task_menu"
    },
    "task_due_date_prompt": {
        "text_input": {
            "next_state": "task_menu"
        },
        "/cancel": "task_menu"
    },
    "task_priority_prompt": {
        "text_input": {
            "next_state": "task_menu",
            "actions": ["update_task_priority(text)"],
            "validation": "priority in [1,2,3]"
        },
        "/cancel": "task_menu"
    },
    "task_all_prompt": {
        "text_input": {
            "next_state": "task_menu",
            "actions": ["update_all_task_fields(text)"]
        },
        "/cancel": "task_menu"
    },

    # === Удаление задачи ===
    "delete_task_confirmation_prompt": {
        "/confirm": {
            "next_state": "default_short",
            "actions": ["delete_task_and_children()"]
        },
        "/cancel": "default_short"
    },

    # === Детальный просмотр ===
    "default_detail": {
        "/back": "ListSubtasks",
        "/home": "default_short",
        "/enter <task_id>": {
            "next_state": "ListSubtasks",
            "actions": ["set_current_task(task_id)", "update_breadcrumbs()"]
        }
    }
}


def validate_transition(current_state: str, command: str, context: dict | None = None, **kwargs):
    # Извлечение базовой команды (без параметров)
    base_command = command.split()[0] if command.startswith('/') else command

    # Проверка существования перехода
    if base_command not in state_transitions.get(current_state, {}):
        return {
            "valid": False,
            "error": f"Command '{base_command}' not available in {current_state}"
        }

    transition = state_transitions[current_state][base_command]

    # Проверка условий для условных переходов
    if isinstance(transition, dict) and "condition" in transition:
        condition_met = evaluate_condition(transition["condition"], context)
        if not condition_met:
            return {
                "valid": False,
                "error": f"Condition not met for {command}",
                "condition": transition["condition"]
            }

    # Определение целевого состояния
    next_state = transition if isinstance(transition, str) else transition.get("next_state", current_state)

    actions = transition.get("actions", []) if isinstance(transition, dict) else []
    for action in actions:
        action_name = action.get("name")
        arguments = []
        for argument in action.get("arguments", []):
            if argument in kwargs:
                arguments.append(kwargs[argument])
        action_name(*arguments)


    return {
        "valid": True,
        "next_state": next_state,
        "actions": transition.get("actions", []) if isinstance(transition, dict) else []
    }


def evaluate_condition(condition, context):
    """Вычисление условий перехода"""
    conditions = {
        "breadcrumbs not empty": lambda ctx: bool(ctx.get('breadcrumbs', [])),
        "task_id exists and accessible": lambda ctx: task_exists(ctx.get('task_id'))
    }
    return conditions.get(condition, lambda _: False)(context)