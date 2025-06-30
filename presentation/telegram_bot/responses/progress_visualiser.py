from shared.logging_decorator import log


@log
def get_progress_bar(progress: float, width: int = 20, filled_char: str = '█', empty_char: str = ' ') -> str:
    """
    Creates a visual progress bar string from a progress float

    Args:
        progress: Completion percentage (0.0 to 1.0)
        width: Character width of progress bar (default: 20)
        filled_char: Character for completed portion (default: '█')
        empty_char: Character for remaining portion (default: ' ')

    Returns:
        Formatted progress bar string e.g. "[█████     ] 50%"
    """
    # Clamp progress between 0.0 and 1.0
    clamped = max(0.0, min(1.0, progress))

    # Calculate filled portion and percentage
    filled_width = int(clamped * width)
    percentage = int(clamped * 100)

    # Build progress bar components
    filled = filled_char * filled_width
    empty = empty_char * (width - filled_width)

    return f"\[{filled}{empty}\] {percentage}%"