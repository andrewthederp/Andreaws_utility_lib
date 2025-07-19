import inspect
from types import UnionType
from inspect import Parameter as InParam
from typing import Any, Union, Literal, Annotated

from utilities.commands.converter import Converter, FlagConverter

empty = InParam.empty


class Parameter(InParam):
    def __init__(self, name: str, kind: Any, default: Any | InParam.empty = empty, annotation: Any = str, description: str | None = None):
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

    def get_completions(self, value: str) -> list[str]:
        annotation = self.annotation
        if origin := getattr(annotation, "__origin__", None):
            return self.get_origin_completions(annotation, origin, value)

        if (inspect.isclass(annotation) and issubclass(annotation, Converter)) or isinstance(annotation, Converter):
            return self.get_annotation_completions(annotation, value)

        return []

    def get_origin_completions(self, annotation, origin, value) -> list[str]:
        # only Literal, Union, Annotated are supported
        if origin is Literal:
            return [str(arg) for arg in annotation.__args__ if str(arg).startswith(value)]
        elif origin is Union or isinstance(origin, UnionType):
            lst: list[str] = []
            for annotation in annotation.__args__:
                if origin := getattr(annotation, "__origin__", None):
                    lst.extend(self.get_origin_completions(annotation, origin, value))
                else:
                    lst.extend(self.get_annotation_completions(annotation, value))
            return lst
        elif origin is Annotated:
            _, annotation = origin.__args__

            if origin := getattr(annotation, "__origin__", None):
                return self.get_origin_completions(annotation, origin, value)
            else:
                return self.get_annotation_completions(annotation, value)
        else:
            raise Exception("Unsupported origin")

    def get_annotation_completions(self, annotation, value) -> list[str]:
        func = getattr(annotation, "get_completions", NotImplemented)
        if func is not NotImplemented:
            return list(func(annotation, value))  # type: ignore

        if (inspect.isclass(annotation) and issubclass(annotation, FlagConverter)) or isinstance(annotation, FlagConverter):
            flag_conv = annotation
            prefix = flag_conv._prefix or " "  # type: ignore
            delimiter = flag_conv._delimiter  # type: ignore

            flags = value.split(prefix)
            latest_flag = flags[-1]

            if delimiter in latest_flag:
                flag_name, _, value = latest_flag.partition(delimiter)
                parameter = flag_conv._flag_parameters.get(flag_name)  # type: ignore

                if not parameter:
                    return []

                annotation = parameter.annotation
                origin = getattr(annotation, "__origin__", None)
                if origin in (list, tuple):
                    annotation = annotation.__args__[0]
                    if origin := getattr(annotation, "__origin__", None):
                        return self.get_origin_completions(annotation, origin, value)
                    else:
                        return self.get_annotation_completions(annotation, value)
                elif origin is None:
                    return self.get_annotation_completions(annotation, value)
                else:
                    return self.get_origin_completions(annotation, origin, value)
            else:
                return [name for name in flag_conv._flag_names if name.startswith(latest_flag)]  # type: ignore

        return []
