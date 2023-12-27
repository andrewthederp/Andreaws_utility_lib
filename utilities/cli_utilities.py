import os

from .color_utilities import convert_to_color, rgb_or_rgba_or_hex_typehint

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
        return_string: bool = False
):
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


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
