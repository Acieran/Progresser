import inspect
import logging
from datetime import datetime
from decimal import Decimal
from functools import wraps
from uuid import UUID


# --- Configuration ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log',
    filemode='w',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

call_count = 0
symbol = "*"


def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global call_count
        # Get function signature and parameter names
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        # Prepare argument representations
        arg_reprs = []
        for name, value in bound.arguments.items():
            arg_reprs.append(
                f"{name} = {safe_repr(value, 3, 100)}"
            )
        # Входные данные
        logger.info(f"{symbol* call_count}Call: {func.__name__} with args={arg_reprs} kwargs={str(kwargs)}")
        call_count += 1
        result = func(*args, **kwargs)
        # Выходные данные
        logger.info(f"{symbol* (call_count-1)}Done: {func.__name__} result={result}")
        call_count-=1
        return result
    return wrapper

def log_exception(e, func_name):
    logger.exception(f"{func_name} produced exception - {e}")

def log_business_error(e, func_name):
    logger.warning(f"{func_name} produced business error - {e}")


def safe_repr(obj, max_depth: int, max_length: int, _current_depth: int = 0) -> str:
    """Recursively create safe string representations of objects"""
    if _current_depth >= max_depth:
        return "..."  # Depth limit reached

    # Handle None and simple types
    if obj is None:
        return "None"

    # Handle common types with safe representations
    if isinstance(obj, (int, float, bool, complex, Decimal, UUID)):
        return str(obj)

    # Handle strings with length limit
    if isinstance(obj, str):
        return f'"{obj[:max_length]}{"..." if len(obj) > max_length else ""}"'

    # Handle datetime objects
    if isinstance(obj, datetime):
        return f"datetime({obj.isoformat(timespec='seconds')})"

    # Handle bytes
    if isinstance(obj, bytes):
        return f"bytes({len(obj)})"

    # Handle collections
    if isinstance(obj, (list, tuple, set, frozenset)):
        items = []
        for item in list(obj)[:max_length]:
            items.append(safe_repr(item, max_depth, max_length, _current_depth + 1))
        suffix = ", ..." if len(obj) > max_length else ""

        if isinstance(obj, tuple):
            return f"({', '.join(items)}{suffix})"
        if isinstance(obj, set):
            return f"{{{', '.join(items)}{suffix}}}"
        return f"[{', '.join(items)}{suffix}]"

    # Handle dictionaries
    if isinstance(obj, dict):
        items = []
        for i, (k, v) in enumerate(obj.items()):
            if i >= max_length:
                break
            key_repr = safe_repr(k, max_depth, max_length, _current_depth + 1)
            val_repr = safe_repr(v, max_depth, max_length, _current_depth + 1)
            items.append(f"{key_repr}: {val_repr}")
        suffix = ", ..." if len(obj) > max_length else ""
        return f"{{{', '.join(items)}{suffix}}}"

    # Handle custom objects
    if hasattr(obj, '__dict__'):
        try:
            # Get public attributes
            attrs = {}
            for k, v in vars(obj).items():
                if not k.startswith('_'):
                    attrs[k] = v

            # Format as class representation
            class_name = obj.__class__.__name__
            attr_reprs = []
            for k, v in list(attrs.items())[:max_length]:
                attr_reprs.append(
                    f"{k}={safe_repr(v, max_depth, max_length, _current_depth + 1)}"
                )
            suffix = ", ..." if len(attrs) > max_length else ""
            return f"{class_name}({', '.join(attr_reprs)}{suffix})"
        except Exception:
            pass

    # Fallback to type-based representation
    return f"<{obj.__class__.__name__} at 0x{id(obj):x}>"