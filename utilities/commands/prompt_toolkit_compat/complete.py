import prompt_toolkit  # type: ignore

import typing
import inspect
from types import UnionType
from contextlib import suppress

from prompt_toolkit.completion import CompleteEvent, Completer, Completion  # type: ignore
from prompt_toolkit.document import Document  # type: ignore
from utilities.commands import Command, Converter, FlagConverter, StringView, get_command_list


class CommandCompleter(Completer):
    pos: int = 0

    def get_completions(self, document: Document, complete_event: CompleteEvent):
        if not document.text:
            for cmd in get_command_list():
                yield Completion(cmd.names[0], start_position=self.pos)
            return

        if document.text[-1] == " ":
            return []

        view = StringView(document.text)

        command: Command | None = None
        last_arg = ""
        command_list = get_command_list()

        try:
            while command is None or command.children:
                command_dict = {}
                last_arg = view.get_next_word()

                for command_obj in command_list:
                    for name in command_obj.names:
                        command_dict[name] = command_obj

                _command: Command | None = command_dict.get(last_arg)
                if _command:
                    command = _command

                    if command.children:  # type: ignore
                        command_list = command.children  # type: ignore
                else:
                    break
        except IndexError:
            pass

        completions = []
        if command:
            for child in command.children:
                for name in child.names:
                    if name.startswith(last_arg):
                        completions.append(name)

            # autocomplete_dict = getattr(command, "_autocomplete", {})
            with suppress(IndexError):
                # TODO: improve!
                for param in command.parameters[command.pass_context:]:
                    if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                        last_arg = view.get_next_word()
                    elif param.kind == inspect.Parameter.KEYWORD_ONLY:
                        last_arg = view.get_rest()
                        if not last_arg:
                            continue

                    self.pos = -len(last_arg)

                    completions = param.get_completions(last_arg)
                    if (inspect.isclass(param.annotation) and issubclass(param.annotation, FlagConverter)) or isinstance(param.annotation, FlagConverter):
                        flag_conv = param.annotation
                        prefix = flag_conv._prefix or " "  # type: ignore
                        delimiter = flag_conv._delimiter  # type: ignore

                        flags = last_arg.split(prefix)
                        latest_flag = flags[-1]
                        if delimiter in latest_flag:
                            _, _, value = latest_flag.partition(delimiter)
                            self.pos = -len(value)
                        else:
                            self.pos = -len(latest_flag)
        elif command_list:
            self.pos = -len(last_arg)
            completions = [name for command in command_list for name in command.names if name.startswith(last_arg)]

        for completion in completions:
            yield Completion(completion, start_position=self.pos)

        return []
