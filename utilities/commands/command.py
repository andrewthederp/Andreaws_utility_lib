from __future__ import annotations

import inspect

from utilities.commands.converter import async_convert, convert
from utilities.commands.errors import CommandNotFound, MissingRequiredArgument
from utilities.commands.parameter import Parameter
from utilities.commands.view import StringView
from utilities.misc import maybe_await
from typing import Callable


def evaluate_annotation(annotation, globals):
    if isinstance(annotation, str):
        return eval(annotation, globals)

    return annotation


class Command:
    def __init__(
            self,
            callback: Callable,
            *,
            name: str | None = None,
            description: str = '',
            usage: str = '',
            aliases: list[str] | None = None,
            parent: Command | None = None,
            pass_context: bool = False
    ):
        self.names: list[str] = [name or callback.__name__] + (aliases or [])
        self.usage: str = usage
        self.description: str = description
        self.callback: Callable = callback
        self.parameters: list[Parameter] = []
        self.pass_context = pass_context

        for name, param in inspect.signature(self.callback).parameters.items():
            if isinstance(param.default, Parameter):
                self.parameters.append(param.default)
            else:
                parameter = Parameter(
                    name=name,
                    kind=param.kind,
                    default=param.default,
                    annotation=str if param.annotation is inspect.Parameter.empty else evaluate_annotation(param.annotation, callback.__globals__)
                )
                self.parameters.append(parameter)

        self.parent: Command | None = parent
        self.children: list[Command] = []

        self.execute = self.async_execute if inspect.iscoroutinefunction(self.callback) else self.sync_execute

    def __repr__(self):
        return f'<Command name="{self.names[0]}">'

    def command(self, *args, **kwargs):
        def decorator(func):
            command = Command(func, *args, parent=self, **kwargs)
            self.children.append(command)
            return command

        return decorator

    def sync_execute(self, view: StringView, *, context=None):
        if self.children and not view.eof:
            name = view.get_next_word()
            for child in self.children:
                if name in child.names:
                    child.sync_execute(view, context=context)  # if the parent is sync I'll safely assume the child is too
                    return
            view.undo()

        args = []
        kwargs = {}

        if context is not None:
            args.append(context)

        for i, param in enumerate(self.parameters[bool(context is not None):]):
            if param.kind == Parameter.POSITIONAL_ONLY or param.kind == Parameter.POSITIONAL_OR_KEYWORD:
                try:
                    arg = view.get_next_word()
                    value = convert(arg, view, param.annotation, context=context)
                except IndexError:
                    if param.required:
                        raise MissingRequiredArgument(param)
                    else:
                        value = param.default

                args.append(value)
            elif param.kind == Parameter.VAR_POSITIONAL:
                while not view.eof:
                    arg = view.get_next_word()
                    value = convert(arg, view, param.annotation, context=context)
                    args.append(value)
            elif param.kind == Parameter.KEYWORD_ONLY:
                arg = view.get_rest()
                if not arg:
                    if param.required:
                        raise MissingRequiredArgument(param)
                    else:
                        kwargs[param.name] = param.default
                else:
                    value = convert(arg, view, param.annotation, context=context)
                    kwargs[param.name] = value

        self.callback(*args, **kwargs)

    async def async_execute(self, view: StringView, *, context=None):
        if self.children and not view.eof:
            name = view.get_next_word()
            for child in self.children:
                if name in child.names:
                    await child.async_execute(view, context=context)  # if the parent is async I'll safely assume the child is too
                    return
            view.undo()

        args = []
        kwargs = {}

        if context is not None:
            args.append(context)

        for i, param in enumerate(self.parameters[bool(context is not None):]):
            if param.kind == Parameter.POSITIONAL_ONLY or param.kind == Parameter.POSITIONAL_OR_KEYWORD:
                try:
                    arg = view.get_next_word()
                    value = await async_convert(arg, view, param.annotation, context=context)
                except IndexError:
                    if param.required:
                        raise MissingRequiredArgument(param)
                    else:
                        value = param.default

                args.append(value)
            elif param.kind == Parameter.VAR_POSITIONAL:
                while not view.eof:
                    arg = view.get_next_word()
                    value = await async_convert(arg, view, param.annotation, context=context)
                    args.append(value)
            elif param.kind == Parameter.KEYWORD_ONLY:
                arg = view.get_rest()
                if not arg:
                    if param.required:
                        raise MissingRequiredArgument(param)
                    else:
                        kwargs[param.name] = param.default
                else:
                    value = await async_convert(arg, view, param.annotation, context=context)
                    kwargs[param.name] = value

        await maybe_await(self.callback, *args, **kwargs)


_command_list: list[Command] = []


def get_command_list() -> list[Command]:
    # Note: The list will not contain sub commands
    return _command_list


def add_command(command: Command) -> Command:
    _command_list.append(command)
    return command


def remove_command(command: Command | str) -> Command:
    if isinstance(command, Command):
        _command_list.remove(command)
    else:
        for cmd in _command_list[::-1]:
            if command in cmd.names:
                _command_list.remove(cmd)
                command = cmd

    return command  # type: ignore


def command(*args, **kwargs):
    def decorator(func) -> Command:
        command = Command(func, *args, **kwargs)
        add_command(command)
        return command

    return decorator


def process_commands(string: str, *, context=None):
    view = StringView(string)
    name = view.get_next_word()

    command = None
    for cmd in _command_list:
        if name in cmd.names:
            command = cmd
            break

    if command is None:
        raise CommandNotFound(name)

    return command.execute(view, context=context)  # type: ignore
