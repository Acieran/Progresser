from presentation.telegram_bot.in_message_handlers import InMessageHandler
from shared.logging_decorator import log


@log
def parse_deep_link(in_message_handler: InMessageHandler, message):
    params = message.text.split()[1:] if len(message.text.split()) > 1 else []

    if params:
        if params[0] == '/create_task':
            message.text = " ".join(params)
            in_message_handler.create_in_message_task_handler(message)
        elif params[0] == '/delete_task':
            message.text = " ".join(params)
            in_message_handler.delete_task_handler(message)
        elif params[0] == '/edit_task':
            message.text = " ".join(params)
            in_message_handler.edit_in_message_task_handler(message)
