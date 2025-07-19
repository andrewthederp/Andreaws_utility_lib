from __future__ import annotations

import inspect
import arcade
from typing import Callable, TypedDict, Any
import arcade.clock
from pyglet.graphics import Batch
import arcade.shape_list


__all__ = (
    # "DoNotShow",
    "DebugLine",
    "DebugScreen",
)


# TODO: Make more effiecient background color

# class DoNotShow:
#     def __bool__(self):
#         return False

#     def __str__(self):
#         return str()

#     def __int__(self):
#         return int()


# class FontSettings(TypedDict):
#     color: tuple[int, int, int]
#     font_name: str
#     font_size: int
#     underline: bool
#     italic: bool
#     bold: bool


# class DebugLine:
#     def __init__(
#             self,
#             key: str,
#             value: value_callable_typehint | None = None,
#             *,
#             font_name: str | None = None,
#             font_size: int | None = None,
#             color: tuple[int, int, int] | None = None,
#             key_color: tuple[int, int, int] | None = None,
#             value_color: tuple[int, int, int] | None = None,
#             bg_color: tuple[int, int, int] | None = None
#     ):
#         if inspect.isfunction(key):  # Can't decide whether to stick with this impl or remove the ability to provide key per debug line
#             self.key = None
#             self.value = key
#         else:
#             self.key = key
#             self.value = value

#         self.font_name = font_name
#         self.font_size = font_size

#         self.color = color
#         self.key_color = key_color
#         self.value_color = value_color
#         self.bg_color = bg_color

#     def __call__(self):
#         if callable(self.value):
#             return self.value()
#         return self.value

#     def draw(self,
#              y: int,
#              *,
#              key: str,
#              default_color: tuple[int, int, int],
#              default_bg_color: tuple[int, int, int],
#              default_font_name: str,
#              default_font_size: int,
#              batch
#             ) -> int:
#         key_color = self.key_color or self.color or default_color
#         value_color = self.value_color or self.color or default_color
#         bg_color = self.bg_color or default_bg_color

#         font_name = self.font_name or default_font_name
#         font_size = self.font_size or default_font_size

#         # screen = pygame.display.get_surface()

#         value = self.value() if callable(self.value) else self.value
#         if value == DoNotShow or isinstance(value, DoNotShow):
#             return 0

#         # key_surface = font.render(f'{self.key or key}: ', antialias, key_color, bgcolor=bg_color)
#         # value_surface = font.render(repr(value), antialias, value_color, bgcolor=bg_color)

#         # screen.blit(key_surface, (0, y))
#         # screen.blit(value_surface, (key_surface.width, y))

#         # return max(key_surface.height, value_surface.height)
#         key_text = arcade.Text(f"{key}: ", 0, y, key_color, font=font_name, font_size=font_size, batch=batch, anchor_y="top")
#         value_text = arcade.Text(repr(value), key_text.content_width, y, value_color, font=font_name, font_size=font_size, batch=batch, anchor_y="top")

#         return max(key_text.content_height, value_text.content_height)


class DebugLine:
    def __init__(self, key_text: arcade.Text, value_text: arcade.Text, func: Callable):
        self.key_text = key_text
        self.value_text = value_text

        self.func = func

    def update(self):
        self.value_text.text = repr(self.func())

    @property
    def height(self):
        return max(self.key_text.content_height, self.value_text.content_height)

    @property
    def y(self):
        return self.key_text.y

    @y.setter
    def y(self, new_y):
        self.key_text.y = new_y
        self.value_text.y = new_y


class DebugScreen(dict):
    def __init__(
            self,
            *,
            font_name: str,
            font_size: int = 12,
            color: tuple[int, int, int] = (0, 0, 0),
            key_color: tuple[int, int, int] | None = None,
            value_color: tuple[int, int, int] | None = None,
            bg_color: tuple[int, int, int] | None = None,
            do_draw: bool = False
    ):
        super().__init__({})

        self.font_name = font_name
        self.font_size = font_size

        self.do_draw: bool = do_draw

        self.color = color
        self.key_color = key_color
        self.value_color = value_color
        self.bg_color = bg_color

        self.batch = Batch()
        self.y = arcade.get_window().height

    def __delitem__(self, key):
        self.pop(key)

    def __setitem__(self, key, value):
        replace = key in self
        y = self[key].key_text.y if replace else self.y 

        if isinstance(value, DebugLine):
            value.key_text.batch = self.batch
            value.value_text.batch = self.batch

            value.key_text.anchor_y = "top"
            value.value_text.anchor_y = "top"

            value.key_text.y = y
            value.value_text.y = y

            super().__setitem__(key, value)

            if not replace:
                self.y -= max(value.key_text.content_height, value.value_text.content_height)
            return

        key_color = self.key_color or self.color
        value_color = self.value_color or self.color

        key_text = arcade.Text(
                f"{key}: ",
                0,
                y,
                key_color,
                self.font_size,
                font_name=self.font_name,
                anchor_y="top",
                batch=self.batch
            )

        value_text = arcade.Text(
                repr(value()),
                key_text.content_width,
                y,
                value_color,
                self.font_size,
                font_name=self.font_name,
                anchor_y="top",
                batch=self.batch
            )

        if not replace:
            self.y -= max(key_text.content_height, value_text.content_height)

        super().__setitem__(
            key,
            DebugLine(
                key_text=key_text,
                value_text=value_text,
                func=value
            )
        )

    def pop(self, key):
        try:
            debug_line: DebugLine = super().pop(key)
        except KeyError:
            return False

        debug_line.key_text.batch = None  # type: ignore
        debug_line.value_text.batch = None  # type: ignore

        y = debug_line.key_text.top
        h = max(debug_line.key_text.content_height, debug_line.value_text.content_height)

        for debug_line in [dgl for dgl in self.values() if dgl.key_text.top < y]:
            debug_line.key_text.y += h
            debug_line.value_text.y += h

        return True

    def adjust_positions(self):
        y = arcade.get_window().height

        for debug_line in self.values():
            debug_line.y = y
            y -= debug_line.height

        self.y = y

    def draw(self):
        if self.do_draw is False:
            return

        for value in self.values():
            value.update()

            if self.bg_color:
                arcade.draw_lrbt_rectangle_filled(
                    value.key_text.left,
                    value.value_text.right,
                    value.key_text.bottom,
                    value.value_text.top,
                    self.bg_color
                )

        self.batch.draw()
