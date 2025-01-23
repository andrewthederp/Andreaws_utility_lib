import os
from typing import Tuple
from .color_utilities import convert_to_color, rgb_or_rgba_or_hex_typehint
from .math_utilities import color_lerp

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
        fg_color: rgb_or_rgba_or_hex_typehint = False,
        bg_color: rgb_or_rgba_or_hex_typehint = False,
        return_string: bool = False,
) -> str | None:
    string = ''

    if fg_color:
        r, g, b, a = convert_to_color(fg_color)
        string = f'\033[38;2;{int(r * a)};{int(g * a)};{int(b * a)}m'
    if bg_color:
        r, g, b, a = convert_to_color(bg_color)
        string += f'\033[48;2;{int(r * a)};{int(g * a)};{int(b * a)}m'

    if return_string:
        return string + text + RESET
    else:
        print(string + text + RESET)


def print_gradient(
        text: str,
        start_fg_color: Tuple[int, int, int] = False,
        end_fg_color: Tuple[int, int, int] = False,
        start_bg_color: Tuple[int, int, int] = False,
        end_bg_color: Tuple[int, int, int] = False,
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

        if start_fg_color:
            fg_rgb = color_lerp(start_fg_color, end_fg_color, i / len(text))
        if start_bg_color:
            bg_rgb = color_lerp(start_bg_color, end_bg_color, i / len(text))

        string += print_rgb(letter, fg_color=fg_rgb, bg_color=bg_rgb, return_string=True).rstrip(RESET)

    string += RESET

    if return_string:
        return string
    else:
        print(string)


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
