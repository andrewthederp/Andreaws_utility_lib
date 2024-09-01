from __future__ import annotations

import inspect

from utilities.misc import maybe_await
from utilities.commands.view import StringView
from utilities.commands.parameter import Parameter
from utilities.commands.converter import convert, async_convert
from utilities.commands.errors import MissingRequiredArgument, CommandNotFound, ConversionError


class Command:
    def __init__(
            self,
            callback: callable,
            *,
            name: str = None,
            description: str = '',
            usage: str = '',
            aliases: list[str] = None,
            parent: Command | None = None
    ):
        self.names: list[str] = [name or callback.__name__] + (aliases or [])
        self.usage: str = usage
        self.description: str = description
        self.callback: callable = callback
        self.parameters: list[Parameter] = []

        for name, param in inspect.signature(self.callback).parameters.items():
            if isinstance(param.default, Parameter):
                self.parameters.append(Parameter)
            else:
                parameter = Parameter(
                    name=name,
                    kind=param.kind,
                    default=None if param.default is inspect.Parameter.empty else param.default,
                    annotation=str if param.annotation is inspect.Parameter.empty else param.annotation
                )
                self.parameters.append(parameter)

        self.parent: Command | None = parent
        self.children: list[Command] = []

    def __repr__(self):
        return f'<Command name="{self.names[0]}">'

    def command(self, *args, **kwargs):
        def decorator(func):
            command = Command(func, *args, parent=self, **kwargs)
            self.children.append(command)
            return command

        return decorator

    def execute(self, view: StringView, *, context=None):
        if self.children and not view.eof:
            name = view.get_next_word()
            for child in self.children:
                if name in child.names:
                    child.execute(view, context=context)
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
                    await child.async_execute(view, context=context)
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
    return command


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

    command.execute(view, context=context)


async def async_process_commands(string: str, *, context=None):
    view = StringView(string)
    name = view.get_next_word()

    command = None
    for cmd in _command_list:
        if name in cmd.names:
            command = cmd
            break

    if command is None:
        raise CommandNotFound(name)

    await command.async_execute(view, context=context)
