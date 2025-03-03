from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utilities.commands import Parameter


class ConversionError(Exception):
    """An exception raised whenever an error occurs during conversion"""


class MissingRequiredArgument(Exception):
    """An error raised when there are missing arguments"""

    def __init__(self, missing_arg: Parameter):
        self.missing_arg = missing_arg


class CommandNotFound(Exception):
    """An error raised when no matches the provided name"""

    def __init__(self, name: str):
        self.name = name
