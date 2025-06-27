from __future__ import annotations
import asyncio
import functools
import typing
from inspect import isawaitable
from typing import Optional, Iterable


# def run_in_executor():
#     def decorator(func):
#         @functools.wraps(func)
#         async def wrapper(*args, **kwargs):
#             partial = functools.partial(func, *args, **kwargs)
#             loop = asyncio.get_event_loop()
#             out = loop.run_in_executor(None, partial)
#             if isawaitable(out):
#                 return await out
#             else:
#                 return out
#
#         return wrapper
#
#     return decorator


class TableFormat:
    DOWN_RIGHT = "\u250F"
    DOWN_HORIZONTAL = "\u2533"
    DOWN_LEFT = "\u2513"

    VERTICAL_RIGHT = "\u2523"
    VERTICAL_HORIZONTAL = "\u254B"
    VERTICAL_LEFT = "\u252B"

    UP_RIGHT = "\u2517"
    UP_HORIZONTAL = "\u253B"
    UP_LEFT = "\u251B"

    HORIZONTAL = "\u2501"
    VERTICAL = "\u2503"


def run_in_executor(func):
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        f = functools.partial(func, *args, **kwargs)
        out = await loop.run_in_executor(None, f)
        if isawaitable(out):
            return await out
        else:
            return out

    return wrapper


async def maybe_await(func, *args, **kwargs):
    out = func(*args, **kwargs)

    if isawaitable(out):
        out = await out

    return out


def chunk(iterable, *, chunk_size):
    return [iterable[i:i + chunk_size] for i in range(0, len(iterable), chunk_size)]


def set_global_variable(name, value):
    globals()[name] = value


def get_global_variable(name):
    return globals()[name]


class Tabulate:
    def __init__(self, *, columns: list[str], table_format: type[TableFormat] = TableFormat):
        self.rows = [self._do_row_magic(columns)]
        self.table_format = table_format

    @staticmethod
    def _do_row_magic(row_data):
        max_height = max(i.count("\n") for i in row_data) + 1
        row_data = [row.split('\n') for row in row_data]

        for i, x in enumerate(row_data):
            if len(x) < max_height:
                temp = [""] * max_height
                start_index = (max_height - len(x)) // 2
                for j in range(start_index, start_index + len(x)):
                    temp[j] = x[j - start_index]
                row_data[i] = temp

        return row_data

    def add_row(self, row_data: list[str]) -> Tabulate:
        if len(row_data) != (column_count := len(self.rows[0])):
            raise ValueError(f"row data must be {column_count} columns big!")

        row_data = self._do_row_magic(row_data)
        self.rows.append(row_data)
        return self

    def format(self, table_format: type[TableFormat] | None = None, *, format_string: typing.Callable[[str, int], str] = str.center) -> str:
        table_format: type[TableFormat] = table_format or self.table_format
        widths: list[int] = [max(max(len(section) for section in row[i]) for row in self.rows) for i in range(len(self.rows[0]))]
        heights: list[int] = [max(len(section) for section in row) for row in self.rows]

        start_sep = table_format.DOWN_HORIZONTAL.join(table_format.HORIZONTAL * (w + 2) for w in widths)
        in_sep = start_sep.replace(table_format.DOWN_HORIZONTAL, table_format.VERTICAL_HORIZONTAL)
        end_sep = start_sep.replace(table_format.DOWN_HORIZONTAL, table_format.UP_HORIZONTAL)

        string = table_format.DOWN_RIGHT + start_sep + table_format.DOWN_LEFT + "\n"
        for row_count, row in enumerate(self.rows, start=1):
            height = heights[row_count - 1]

            for i in range(height):
                string += table_format.VERTICAL

                for n, cell in enumerate(row):
                    string += format_string(cell[i], widths[n] + 2)

                    string += table_format.VERTICAL

                string += "\n"

            if row_count == len(self.rows):
                string += table_format.UP_RIGHT + end_sep + table_format.UP_LEFT
            else:
                string += table_format.VERTICAL_RIGHT + in_sep + table_format.VERTICAL_LEFT

            string += "\n"

        return string

    def __str__(self):
        return self.format()


def multi_split(string: str, *split_on: str):
    lst = []
    temp = ""
    temp2 = ""
    for char in string:
        possible_matches = [i for i in split_on if i.startswith(temp2 + char)]

        if possible_matches:
            temp2 += char
            if temp2 in possible_matches:
                lst.append(temp)
                temp = ""
                temp2 = ""
        else:
            temp += char

    lst.append(temp)
    return lst
