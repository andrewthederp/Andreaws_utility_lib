import inspect
from typing import Annotated, Any, Literal, Union

from utilities.commands.errors import ConversionError
from utilities.commands.view import StringView
from utilities.misc import maybe_await


class Converter:
    def convert(self, argument: str, view: StringView, context: Any):
        raise NotImplementedError


class BoolConverter(Converter):
    def convert(self, argument: str, _: StringView, __):
        argument = argument.lower()

        if argument in ["1", "yes", "y"]:
            return True
        elif argument in ["0", "no", "n"]:
            return False
        else:
            raise ConversionError(f"{argument} could not be converted into a bool")


def handle_origin(argument: str, view: StringView, annotation: Any, origin: Any, context):
    if origin is Union:
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
    if origin is Union:
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


def convert(argument: str, view: StringView, annotation: Any, context=None):
    if annotation is bool:
        annotation = BoolConverter

    annotation: Converter | callable

    if origin := getattr(annotation, "__origin__", None):
        return handle_origin(argument, view, annotation, origin, context)

    try:
        if annotation in [str, int, float]:
            return annotation(argument)
        elif isinstance(annotation, Converter):
            return annotation.convert(argument, view, context)
        elif inspect.isclass(annotation) and issubclass(annotation, Converter):
            return annotation().convert(argument, view, context)
        elif inspect.isfunction(annotation):
            return annotation(argument, view, context)
    except Exception as e:
        raise ConversionError(e)


async def async_convert(argument: str, view: StringView, annotation: Any, context=None):
    if annotation is bool:
        annotation = BoolConverter

    annotation: Converter | callable

    if origin := getattr(annotation, "__origin__", None):
        return await async_handle_origin(argument, view, annotation, origin, context)

    try:
        if annotation in [str, int, float]:
            return annotation(argument)
        elif isinstance(annotation, Converter):
            return await maybe_await(annotation.convert, argument, view, context)
        elif inspect.isclass(annotation) and issubclass(annotation, Converter):
            return await maybe_await(annotation().convert, argument, view, context)
        elif inspect.isfunction(annotation):
            return await maybe_await(annotation, argument, view, context)
    except Exception as e:
        raise ConversionError(e)
