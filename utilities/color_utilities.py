import json
import re
from typing import Tuple, Union

hex_typehint = Union[str, int]
rgb_or_rgba_typehint = Union[Tuple[int, int, int], Tuple[int, int, int, float]]
rgb_or_rgba_or_hex_typehint = Union[hex_typehint, rgb_or_rgba_typehint]

RGB_PATTERN = re.compile(r"\(?(\d+),\s?(\d+),\s?(\d+)(,\s?(\d+))?\)?")

with open("data/colors.json", "r") as f:
    COLORS = json.load(f)


def convert_to_color(color: rgb_or_rgba_or_hex_typehint, *, return_hex: bool = False):
    if isinstance(color, (tuple, list)):
        red = color[0]
        green = color[1]
        blue = color[2]
        if len(color) == 4:
            alpha = color[3]
        else:
            alpha = 1

    else:
        if isinstance(color, str):
            if color in COLORS:
                red, green, blue = COLORS[color]
                if return_hex:
                    return hex_from_rgb(red, green, blue)
                return red, green, blue
            elif match := RGB_PATTERN.search(color):
                colors = tuple(int(val) for val in match.groups() if val)
                red = colors[0]
                green = colors[1]
                blue = colors[2]
                if len(colors) == 4:
                    alpha = colors[3]
                else:
                    alpha = 1

                if return_hex:
                    return hex_from_rgb(red, green, blue)
            else:
                if return_hex:
                    return color  # why would you pass a hex and ask for a hex back
                color = color.lower().replace("0x", '').replace("#", '')
                color = int(color, base=16)

        if isinstance(color, int):
            red = (color >> 16) & 0xFF
            green = (color >> 8) & 0xFF
            blue = color & 0xFF
            alpha = 1

    if return_hex:
        return hex_from_rgb(red, green, blue, alpha)

    return red, green, blue, alpha


def hex_from_rgb(red: int, green: int, blue: int, alpha: float = 1) -> str:
    return f"#{red:02x}{green:02x}{blue:02x}"
