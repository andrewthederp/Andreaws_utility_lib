from __future__ import annotations

import inspect
import pygame
from typing import Callable, Any


__all__ = (
    "DoNotShow",
    "DebugLine",
    "DebugScreen",
)


class DoNotShow:
    def __bool__(self):
        return False

    def __str__(self):
        return str()

    def __int__(self):
        return int()


value_callable_typehint = Any | Callable[[], str | type[DoNotShow] | DoNotShow]


class DebugLine:
    def __init__(
            self,
            key: str,
            value: value_callable_typehint | None = None,
            *,
            font: pygame.Font | None = None,
            color: tuple[int, int, int] | None = None,
            key_color: tuple[int, int, int] | None = None,
            value_color: tuple[int, int, int] | None = None,
            bg_color: tuple[int, int, int] | None = None
    ):
        if inspect.isfunction(key):  # Can't decide whether to stick with this impl or remove the ability to provide key per debug line
            self.key = None
            self.value = key
        else:
            self.key = key
            self.value = value

        self.font = font

        self.color = color
        self.key_color = key_color
        self.value_color = value_color
        self.bg_color = bg_color

    def __call__(self):
        if callable(self.value):
            return self.value()
        return self.value

    def draw(self, y: int, *, key: str, default_color: tuple[int, int, int], default_bg_color: tuple[int, int, int] | None, default_font: pygame.Font, antialias: bool = True) -> int:
        key_color = self.key_color or self.color or default_color
        value_color = self.value_color or self.color or default_color
        bg_color = self.bg_color or default_bg_color

        font = self.font or default_font

        screen = pygame.display.get_surface()

        value = self.value() if callable(self.value) else self.value
        if value == DoNotShow or isinstance(value, DoNotShow):
            return 0

        key_surface = font.render(f'{self.key or key}: ', antialias, key_color, bgcolor=bg_color)
        value_surface = font.render(repr(value), antialias, value_color, bgcolor=bg_color)

        screen.blit(key_surface, (0, y))
        screen.blit(value_surface, (key_surface.width, y))

        return max(key_surface.height, value_surface.height)


class DebugScreen(dict):
    def __init__(
            self,
            *,
            data: dict[str, value_callable_typehint | DebugLine] = {},
            font: pygame.Font | None = None,
            font_size: int | None = None,
            color: tuple[int, int, int] = (0, 0, 0),
            key_color: tuple[int, int, int] | None = None,
            value_color: tuple[int, int, int] | None = None,
            bg_color: tuple[int, int, int] | None = None,
            do_draw: bool = False
    ):
        super().__init__(data)

        if font is None and font_size is None:
            raise TypeError("You must provide a font_size if you do not provide a font")

        if font is None:
            self.font = pygame.font.SysFont(pygame.font.get_fonts()[0], font_size)
        else:
            self.font = font

        self.do_draw: bool = do_draw

        self.color = color
        self.key_color = key_color
        self.value_color = value_color
        self.bg_color = bg_color

    def draw(self, *, antialias: bool = True):
        if self.do_draw is False:
            return

        screen = pygame.display.get_surface()
        y = 0

        for key, value in self.items():
            if isinstance(value, DebugLine):
                y += value.draw(y, key=key, antialias=antialias, default_color=self.color, default_bg_color=self.bg_color, default_font=self.font)
            else:
                value = value() if callable(value) else value
                if value == DoNotShow or isinstance(value, DoNotShow):
                    continue

                key_color = self.key_color or self.color
                value_color = self.value_color or self.color

                key_surface = self.font.render(f'{key}: ', antialias, key_color, bgcolor=self.bg_color)
                value_surface = self.font.render(repr(value), antialias, value_color, bgcolor=self.bg_color)

                screen.blit(key_surface, (0, y))
                screen.blit(value_surface, (key_surface.width, y))

                y += max(key_surface.height, value_surface.height)
