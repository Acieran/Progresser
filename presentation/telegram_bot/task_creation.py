from shared.logging_decorator import log


class TaskCreation:
    def __init__(self, telegram_username):
        self.telegram_username = telegram_username

    @log
    def update_task_due_date(self): ...