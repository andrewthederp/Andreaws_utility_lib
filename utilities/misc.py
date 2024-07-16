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


def chunk(iterable, *, chunk_size):
    return [iterable[i:i + chunk_size] for i in range(0, len(iterable), chunk_size)]


def set_global_variable(name, value):
    globals()[name] = value


def get_global_variable(name):
    return globals()[name]


class Tabulate:
    def __init__(self, *, columns: list[str]):
        self.rows = [columns]
        self.widths = [len(i) for i in columns]

    def add_row(self, row_data: list[str]):
        if len(row_data) != (column_count := len(self.widths)):
            raise ValueError(f"row data must be {column_count} columns big!")

        self.rows.append(row_data)
        self.widths = [max(len(str(i)), self.widths[n]) for n, i in enumerate(row_data)]

    def format(self):
        sep = "\u2533".join("\u2501" * (w + 2) for w in self.widths)
        in_sep = "\u254B".join("\u2501" * (w + 2) for w in self.widths)

        string = "\u250F" + sep + "\u2513\n"
        for row_count, row in enumerate(self.rows, start=1):
            string += "\u2503"
            for n, cell in enumerate(row):
                string += cell.center(self.widths[n] + 2)
                string += "\u2503"
            string += "\n"

            if row_count == len(self.rows):
                string += "\u2517" + sep.replace("\u2533", "\u253B") + "\u251B"
            else:
                string += "\u2523" + in_sep + "\u252B"

            string += "\n"

        return string
