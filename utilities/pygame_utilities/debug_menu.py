from __future__ import annotations

import inspect
import pygame
from typing import Callable


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


value_callable_typehint = Callable[[], str | type[DoNotShow] | DoNotShow]


class DebugLine:
    def __init__(
            self,
            key: str,
            value: value_callable_typehint | None = None,
            *,
            font: pygame.Font | None = None,
            color: tuple[int, int, int] | None = None,
            key_color: tuple[int, int, int] | None = None,
            value_color: tuple[int, int, int] | None = None
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

    def __call__(self):
        return self.value()

    def draw(self, y: int, *, key: str, default_color: tuple[int, int, int], default_font: pygame.Font, antialias: bool = True) -> int:
        key_color = self.key_color or self.color or default_color
        value_color = self.value_color or self.color or default_color

        font = self.font or default_font

        screen = pygame.display.get_surface()

        value = self.value()
        if value == DoNotShow or isinstance(value, DoNotShow):
            return 0

        key_surface = font.render(f'{self.key or key}: ', antialias, key_color)
        value_surface = font.render(str(value), antialias, value_color)

        screen.blit(key_surface, (0, y))
        screen.blit(value_surface, (key_surface.width, y))

        return max(key_surface.height, value_surface.height)


class DebugScreen(dict):
    def __init__(
            self,
            *,
            font: pygame.Font | None = None,
            font_size: int | None = None,
            data: dict[str, value_callable_typehint | DebugLine],
            color: tuple[int, int, int] = (0, 0, 0),
            key_color: tuple[int, int, int] | None = None,
            value_color: tuple[int, int, int] | None = None,
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

    def draw(self, *, antialias: bool = True):
        if self.do_draw is False:
            return

        screen = pygame.display.get_surface()
        y = 0

        for key, func in self.items():
            if isinstance(func, DebugLine):
                y += func.draw(y, key=key, antialias=antialias, default_color=self.color, default_font=self.font)
            else:
                value = func()
                if value == DoNotShow or isinstance(value, DoNotShow):
                    continue

                key_color = self.key_color or self.color
                value_color = self.value_color or self.color

                key_surface = self.font.render(f'{key}: ', antialias, key_color)
                value_surface = self.font.render(str(value), antialias, value_color)

                screen.blit(key_surface, (0, y))
                screen.blit(value_surface, (key_surface.width, y))

                y += max(key_surface.height, value_surface.height)
