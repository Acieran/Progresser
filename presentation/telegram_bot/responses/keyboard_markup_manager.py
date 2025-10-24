from telebot import types

reply_markup_dict: dict[str: ...] = {
    "keyboard": types.ReplyKeyboardMarkup(resize_keyboard=True),
    "task_name_prompt": None,
    "task_description_prompt": None,
    "task_priority_prompt": None,
    "task_due_date_prompt": None,
    "task_all_prompt": None,
    "task_name_prompt_edit": None,
    "task_description_prompt_edit": None,
    "task_priority_prompt_edit": None,
    "task_due_date_prompt_edit": None,
    "task_all_prompt_edit": None,
}
for key in state_service.state_transitions.keys():
    if key not in reply_markup_dict.keys():
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*state_service.state_transitions[key].keys(), row_width=3)
        reply_markup_dict[key] = keyboard


# keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
# keyboard.row(
#     types.KeyboardButton('/edit_name'),
#     types.KeyboardButton('/edit_description'),
#     types.KeyboardButton('/edit_due_date')
# )
# keyboard.row(
#     types.KeyboardButton('/edit_priority'),
#     types.KeyboardButton('/confirm_creation'),
#     types.KeyboardButton('/cancel')
# )
# reply_markup_dict["task_menu"] = keyboard
# keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
# keyboard.row(
#     types.KeyboardButton('/edit_name_edit'),
#     types.KeyboardButton('/edit_description_edit'),
#     types.KeyboardButton('/edit_due_date_edit')
# )
# keyboard.row(
#     types.KeyboardButton('/edit_priority_edit'),
#     types.KeyboardButton('/confirm_creation_edit'),
#     types.KeyboardButton('/cancel')
# )
# reply_markup_dict["task_menu"] = keyboard
# keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
# keyboard.row(
#     types.KeyboardButton('/create_task'),
#     types.KeyboardButton('/edit_task'),
#     types.KeyboardButton('/delete_task')
# )
# keyboard.row(
#     types.KeyboardButton('/show_image'),
#     types.KeyboardButton('/enter'),
#     types.KeyboardButton('/back')
# )
# keyboard.row(
#     types.KeyboardButton('/home'),
#     types.KeyboardButton('/next'),
#     types.KeyboardButton('/previous')
# )
# reply_markup_dict["default_short"] = keyboard
# reply_markup_dict["default_detail"] = keyboard
# keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
# keyboard.row(
#     types.KeyboardButton('/confirm'),
#     types.KeyboardButton('/cancel'),
# )
# reply_markup_dict["delete_task_confirmation_prompt"] = keyboard
