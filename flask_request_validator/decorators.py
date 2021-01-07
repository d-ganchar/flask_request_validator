from typing import Any, Callable


def overrides(base_class: Any) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if func.__name__ not in dir(base_class):
            raise AssertionError(f'Base class "{base_class.__name__}" does not have such a method "{func.__name__}".')

        return func
    return decorator
