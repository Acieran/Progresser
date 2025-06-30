from shared.logging_decorator import log


@log
def generate_short_response(
        title: str,
        symbol: str,
        progress_bar: str,
        task_id: int
) -> str:
    text = (
        f"{symbol} {title[:70]:<70}\n"
        f'\<\>[Добавить подзачу](tg://resolve?domain=acie_progresser_bot&text=/create_task {str(task_id)}) '
        f'[Изменить](tg://resolve?domain=acie_progresser_bot&text=/edit_task {str(task_id)}) '
        f'[Удалить](tg://resolve?domain=acie_progresser_bot&text=/delete_task {str(task_id)})'
        f'{progress_bar}'
    )
    return text
