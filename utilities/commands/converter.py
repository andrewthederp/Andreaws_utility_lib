import inspect
import re
from types import UnionType
from typing import Annotated, Any, Literal, Union, Callable, Sequence

from utilities.commands.errors import ConversionError
from utilities.commands.view import StringView
from utilities.misc import maybe_await


class Converter:
    get_completions = NotImplemented

    def convert(self, argument: str, view: StringView, context: Any):
        raise NotImplementedError


class BoolConverter(Converter):
    def convert(self, argument: str, _: StringView, __):
        argument = argument.lower()

        if argument in ["1", "yes", "y", "true"]:
            return True
        elif argument in ["0", "no", "n", "false"]:
            return False
        else:
            raise ConversionError(f"{argument} could not be converted into a bool")


class FlagConverterMetaClass(type):
    def __new__(cls, name, bases, attrs, *, prefix="--", delimiter=" "):
        attrs['_prefix'] = prefix
        attrs['_delimiter'] = delimiter

        names = []
        parameters = {}
        for flag_name, annotation in attrs.get('__annotations__', {}).items():
            names.append(flag_name)

            kwargs = {"annotation": annotation}
            kind = inspect.Parameter.POSITIONAL_ONLY  # whatever
            try:
                default = attrs[flag_name]
                kwargs["default"] = default
            except KeyError:
                pass

            parameters[flag_name] = inspect.Parameter(flag_name, kind, **kwargs)

        attrs['_flag_names'] = names
        attrs['_regex_pattern'] = re.compile(f"(({re.escape(prefix)})(?P<flag>{'|'.join(names)}){re.escape(delimiter)})")
        attrs['_flag_parameters'] = parameters

        return type.__new__(cls, name, bases, attrs)


class FlagConverter(Converter, metaclass=FlagConverterMetaClass):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<{self.__class__.__name__} {' '.join(k+'='+str(v) for k, v in self.__dict__.items())}>"

    def convert(self, argument: str, view: StringView, ctx: Any):
        arguments = {}

        matches = list(self._regex_pattern.finditer(argument))  # type: ignore
        for num, i in enumerate(matches, start=1):
            flag_name = i.group('flag')
            argument_start = i.span()[1]

            if num == len(matches):
                string = argument[argument_start:]
            else:
                next_match = matches[num]
                argument_end = next_match.span()[0]
                string = argument[argument_start:argument_end - 1]

            parameter = self._flag_parameters[flag_name]  # type: ignore
            v = StringView(string)

            origin = getattr(parameter.annotation, "__origin__", None)
            if origin in (list, tuple):
                annotation = parameter.annotation.__args__[0]
                if origin == list:
                    converted = convert(string, v, annotation, ctx)
                    arguments.setdefault(flag_name, []).append(converted)
                elif origin == tuple:
                    lst = []
                    while not v.eof:
                        word = v.get_next_word()
                        converted = convert(word, v, annotation, ctx)
                        lst.append(converted)
                    arguments[flag_name] = lst
            else:
                arguments[flag_name] = convert(string, v, parameter.annotation, ctx)

        for flag_name in self._flag_names:  # type: ignore
            parameter = self._flag_parameters[flag_name]  # type: ignore
            if flag_name not in arguments:
                if parameter.default == inspect.Parameter.empty:
                    raise Exception(f'missing required flag "{flag_name}"')
                else:
                    arguments[flag_name] = parameter.default

        return type(self)(**arguments)


def handle_origin(argument: str, view: StringView, annotation: Any, origin: Any, context):
    if isinstance(origin, UnionType) or origin is Union:
        for converter in annotation.__args__:
            if converter is type(None):
                view.undo()
                return None

            try:
                return convert(argument, view, converter, context)
            except:
                pass

        raise ConversionError(f"{argument} could not be converted")
    elif origin is Annotated:
        annotated_args = annotation.__args__

        if origin := getattr(annotated_args[1], "__origin__", None):
            return handle_origin(argument, view, annotated_args[1], origin, context)
        else:
            return convert(argument, view, annotated_args[1], context)
    elif origin is Literal:
        args = annotation.__args__
        if argument in args:
            return argument
        else:
            raise ConversionError(f"{argument} could not be converted into any literal.")


async def async_handle_origin(argument: str, view: StringView, annotation: Any, origin: Any, context):
    if isinstance(origin, UnionType) or origin is Union:
        for converter in annotation.__args__:
            if converter is type(None):
                view.undo()
                return None

            try:
                return await async_convert(argument, view, converter, context)
            except:
                pass

        raise ConversionError(f"{argument} could not be converted")
    elif origin is Annotated:
        annotated_args = annotation.__args__

        if origin := getattr(annotated_args[1], "__origin__", None):
            return await async_handle_origin(argument, view, annotated_args[1], origin, context)
        else:
            return await async_convert(argument, view, annotated_args[1], context)
    elif origin is Literal:
        args = annotation.__args__
        if argument in args:
            return argument
        else:
            raise ConversionError(f"{argument} could not be converted into any literal.")


def convert(argument: str, view: StringView, annotation: Any, context=None):  # type: ignore
    if annotation is bool:
        annotation = BoolConverter

    annotation: Converter | Callable

    origin = getattr(annotation, "__origin__", None) or (isinstance(annotation, UnionType) and annotation)
    if origin:
        return handle_origin(argument, view, annotation, origin, context)

    try:
        if annotation in [str, int, float]:
            return annotation(argument)  # type: ignore
        elif isinstance(annotation, Converter):
            return annotation.convert(argument, view, context)
        elif inspect.isclass(annotation) and issubclass(annotation, Converter):
            return annotation().convert(argument, view, context)
        elif inspect.isfunction(annotation):
            return annotation(argument, view, context)
    except Exception as e:
        raise ConversionError(e)


async def async_convert(argument: str, view: StringView, annotation: Any, context=None):  # type: ignore
    if annotation is bool:
        annotation = BoolConverter

    annotation: Converter | Callable

    if origin := getattr(annotation, "__origin__", None):
        return await async_handle_origin(argument, view, annotation, origin, context)

    try:
        if annotation in [str, int, float]:
            return annotation(argument)  # type: ignore
        elif isinstance(annotation, Converter):
            return await maybe_await(annotation.convert, argument, view, context)
        elif inspect.isclass(annotation) and issubclass(annotation, Converter):
            return await maybe_await(annotation().convert, argument, view, context)
        elif inspect.isfunction(annotation):
            return await maybe_await(annotation, argument, view, context)
    except Exception as e:
        raise ConversionError(e)
