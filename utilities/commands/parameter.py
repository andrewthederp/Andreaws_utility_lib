from inspect import Parameter
from types import UnionType
from typing import Any, Union

empty = Parameter.empty


class Parameter(Parameter):
    def __init__(self, name: str, kind: Any, default: Any | empty = empty, annotation: Any = str, description: str = None):
        kwargs = {"name": name, "kind": kind, "annotation": annotation}

        if default is empty:
            if isinstance(annotation, UnionType) or getattr(annotation, "__origin__", None) is Union:
                if type(None) in annotation.__args__:
                    kwargs["default"] = None
        else:
            kwargs["default"] = default

        super().__init__(**kwargs)

        self.description = description
        self.required = self.default is empty
