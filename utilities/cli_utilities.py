import os
import sys
from typing import Tuple
from .color_utilities import Color
from .math_utilities import color_lerp
from typing import Callable, TYPE_CHECKING

try:
    import readchar  # type: ignore
except ImportError:
    readchar = None

CURSOR_HIDE = "\033[?25l"
CURSOR_SHOW = "\033[?25h"

CURSOR_UP = "\033[{}F"
CURSOR_DOWN = "\033[{}E"

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
REVERSE = "\033[7m"
HIDDEN = "\033[8m"
STRIKETHROUGH = "\033[9m"
DOUBLE_UNDERLINE = "\033[21m"
OVERLINE = "\033[53m"


def print_rgb(
        text: str,
        fg_color: Color | None = None,
        bg_color: Color | None = None,
        return_string: bool = False,
) -> str | None:
    string = ''

    if fg_color:
        r, g, b, a = fg_color.rgba
        string = f'\033[38;2;{int(r * a)};{int(g * a)};{int(b * a)}m'
    if bg_color:
        r, g, b, a = bg_color.rgba
        string += f'\033[48;2;{int(r * a)};{int(g * a)};{int(b * a)}m'

    if return_string:
        return string + text + RESET
    else:
        print(string + text + RESET)


def print_gradient(
        text: str,
        start_fg_color: Color | None = None,
        end_fg_color: Color | None = None,
        start_bg_color: Color | None = None,
        end_bg_color: Color | None = None,
        return_string: bool = False
) -> str | None:
    if any([start_fg_color, end_fg_color]) and not all([start_fg_color, end_fg_color]):
        raise ValueError("Need to provide both a starting and ending foreground color")

    if any([start_bg_color, end_bg_color]) and not all([start_bg_color, end_bg_color]):
        raise ValueError("Need to provide both a starting and ending background color")

    string = ''
    for i, letter in enumerate(text):
        fg_rgb = False
        bg_rgb = False

        if start_fg_color and end_fg_color:
            fg_rgb = color_lerp(start_fg_color.rgb, end_fg_color.rgb, i / len(text))
        if start_bg_color and end_bg_color:
            bg_rgb = color_lerp(start_bg_color.rgb, end_bg_color.rgb, i / len(text))

        string += print_rgb(letter, fg_color=Color(*fg_rgb) if fg_rgb else None, bg_color=Color(*bg_rgb) if bg_rgb else None, return_string=True).rstrip(RESET)  # type: ignore

    string += RESET

    if return_string:
        return string
    else:
        print(string)


def input_choices(string, *, choices: list[str], on_hover: Callable[[str], str] = (lambda c: c), on_unhover: Callable[[str], str] = (lambda c: c)) -> str:
    if TYPE_CHECKING:
        assert readchar

    print(CURSOR_HIDE)
    index = 0

    if string:
        print(string)

    for i, choice in enumerate(choices):
        if i == index:
            print(on_hover(choice))
        else:
            print(on_unhover(choice))
    print(CURSOR_UP.format(len(choices) + 1))

    while True:
        key = readchar.readkey()
        if key not in (readchar.key.DOWN, readchar.key.UP, readchar.key.ENTER):
            continue

        print(on_unhover(choices[index]), end="")
        if key == readchar.key.DOWN:
            index += 1
            if index == len(choices):
                index = 0
                print(CURSOR_UP.format(len(choices)))
            else:
                print()
        elif key == readchar.key.UP:
            index -= 1
            if index == -1:
                index = len(choices) - 1
                print(CURSOR_DOWN.format(index), end="")
            else:
                print(CURSOR_UP.format(2))
        elif key == readchar.key.ENTER:
            print(CURSOR_DOWN.format(len(choices)-index))
            print(CURSOR_SHOW, end="")
            return choices[index]

        print(f"\033[0K{on_hover(choices[index])}\033[A")

if readchar is None:
    input_choices = NotImplemented  # type: ignore


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
