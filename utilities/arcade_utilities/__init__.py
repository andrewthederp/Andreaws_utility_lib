import arcade
from .debug_menu import *
from .commands import CommandView, CommandContext
from .PiPWindow import PiPWindow, DragRect, DragRectType
from typing import TypedDict, Callable, Any


class FuncToRunData(TypedDict):
    func: Callable[..., None]
    args: list[Any]
    seconds: float
    kwargs: dict[str, Any]


class Scheduler:
    def __init__(self):
        self._to_run: list[FuncToRunData] = []

    def run_in(self, func: Callable[..., None], *args: Any, seconds: float, **kwargs: Any):
        self._to_run.append({
            "func": func,
            "seconds": seconds,
            "args": args,  # type: ignore
            "kwargs": kwargs
        })

    def update(self, time_delta):
        indexes_to_pop = []

        for i, task in enumerate(self._to_run):
            task["seconds"] -= time_delta
            if task["seconds"] <= 0:
                func = task["func"]
                func(*task["args"], **task["kwargs"])
                indexes_to_pop.append(i)

        for i in sorted(indexes_to_pop, reverse=True):
            self._to_run.pop(i)


def listen(event_name: str):
    def inner(func):
        window = arcade.get_window()
        window.register_event_type(event_name)
        window.push_handlers(**{event_name: func})
        return func

    return inner
