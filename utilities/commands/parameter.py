import typing
from inspect import Parameter
from typing import Any, get_args, get_origin, Union

empty = Parameter.empty


class Parameter(Parameter):
    def __init__(self, name: str, kind: Any, default: Any | empty = empty, annotation: Any = str, description: str = None):
        kwargs = {"name": name, "kind": kind, "annotation": annotation}

        if default is empty:
            if origin := get_origin(annotation):
                if origin is Union:
                    if type(None) in get_args(annotation):
                        kwargs["default"] = None
        else:
            kwargs["default"] = default

        super().__init__(**kwargs)

        self.description = description
        self.required = self.default is empty
