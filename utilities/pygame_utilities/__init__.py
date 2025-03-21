import pygame
import math
from typing import TypedDict, Callable, Any
from functools import cache
from .debug_menu import *


class FuncToRunData(TypedDict):
    func: Callable[..., None]
    args: list[Any]
    seconds: int | float
    kwargs: dict[str, Any]


class ResizeableFont:
    def __init__(self, font_path, *, sys_font: bool = False):
        self.font_path = font_path
        self.sys_font = sys_font

    @cache
    def __getitem__(self, size):
        if self.sys_font:
            return pygame.font.SysFont(self.font_path, size)
        else:
            return pygame.font.Font(self.font_path, size)


class Scheduler:  # The reason this is a pygame util is no longer... /shrug
    def __init__(self):
        self._to_run: list[FuncToRunData] = []

    def run_in(self, func: Callable[..., None], *args: Any, seconds: int | float, **kwargs: Any):
        func_to_run: FuncToRunData = {"func": func, "args": args, "seconds": seconds, "kwargs": kwargs}
        self._to_run.append(func_to_run)

    def update(self, time_delta):
        indexes_to_pop = []
        for i, dct in enumerate(self._to_run):
            dct["seconds"] -= time_delta
            if dct["seconds"] <= 0:
                func = dct["func"]
                func(*dct["args"], **dct["kwargs"])
                indexes_to_pop.append(i)

        for index in sorted(indexes_to_pop, reverse=True):
            self._to_run.pop(index)


class FlashingText(pygame.sprite.Sprite):
    def __init__(
            self,
            string: str,
            font: pygame.Font,
            antialias: bool,
            color: tuple[int, int, int],
            *groups: pygame.sprite.Group,
            seconds: int,
            **kwargs: int | tuple[int, int]
    ):
        super().__init__(*groups)
        self.text = string
        self.font = font

        self.color = color
        self.antialias = antialias

        self.end_alpha: int = kwargs.pop("end_alpha", None)
        self.start_alpha: int = kwargs.pop("start_alpha", None)

        if self.end_alpha is None and self.start_alpha is None:
            self.end_alpha = 255
            self.start_alpha = 255
        elif self.end_alpha is None and self.start_alpha is not None:
            self.end_alpha = 0
        elif self.end_alpha is not None and self.start_alpha is None:
            self.start_alpha = 255

        self.original_image = font.render(text=string, antialias=antialias, color=color)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(**kwargs)

        self.kwargs = kwargs

        self.start = pygame.time.get_ticks()
        self.fade_after = seconds * 1000

    def get_alpha(self, perc: float):
        return self.start_alpha + (self.end_alpha - self.start_alpha) * perc

    def update(self):
        now = pygame.time.get_ticks()
        if now >= self.start + self.fade_after:
            self.kill()
            return

        self.image = self.original_image.copy()
        now = pygame.time.get_ticks()

        perc = (now - self.start) / self.fade_after

        self.image.set_alpha(self.get_alpha(perc))

        self.rect = self.image.get_rect(**self.kwargs)


def draw_alpha_rect(surface: pygame.Surface, color: tuple[int, int, int, int], rect: pygame.Rect) -> None:
    x, y = rect.topleft
    surf = pygame.Surface(rect.size).convert_alpha()
    surf.fill(color)

    surface.blit(surf, (x, y))
