from arcade.gui import *  # type: ignore
import pyglet
import arcade
import inspect
import arcade.gui
from arcade.types import Color
from pyglet.event import EVENT_HANDLED, EVENT_UNHANDLED

from typing import Sequence, Any
from utilities.commands import StringView, Command, Converter, FlagConverter, command, get_command_list, process_commands

from contextlib import suppress

try:
    import pyperclip
except ImportError:
    pyperclip = None


class CommandContext:
    def __init__(self, window: arcade.Window, command_view: "CommandView") -> None:
        self.window = window
        self.command_view = command_view

    def send(self, text: Any, *, end: str = "\u2028", **kwargs):
        self.command_view.send_text((text if isinstance(text, str) else repr(text)) + end, **kwargs)


class AutoComplete(arcade.gui.UILayout):
    pad = 5
    complete_amount = 5
    complete_spacing = 5

    def __init__(self, x, y, *, completions: list[str], index: int) -> None:
        self.completions = completions
        self.index = index
        self.completion_num = 0
        self.offset = 0

        children, y = self.get_children()

        super().__init__(x=x, y=y, height=y, width=max(child.content_width for child in children) + self.pad * 2, children=children)
        self.with_padding(all=self.pad)
        self.with_background(color=arcade.types.Color(20, 20, 20, 220))

    def do_layout(self):
        if not self._children:
            return

        y = self.bottom
        for child in self.children[::-1]:
            child.bottom = y
            child.left = self.left + self.pad
            y += child.content_height + self.complete_spacing

    def get_displayed_completions(self, num: int | None = None) -> list[str]:
        num = num or self.complete_amount
        if len(self.completions) <= num:
            return self.completions

        start = self.offset
        end = min(start + num, len(self.completions))
        start = end - num

        return self.completions[start:end]

    def get_children(self) -> tuple[list[arcade.gui.UILabel], int]:
        children = []
        y = 0

        completions = self.get_displayed_completions()
        for i, complete in enumerate(completions):
            child = arcade.gui.UILabel(text=complete, y=y, text_color=arcade.types.Color(223, 192, 101) if i == self.completion_num else arcade.types.Color(180, 180, 180), font_size=20)
            children.append(child)
            y += child.content_height + self.complete_spacing

        return children, int(y)

    def go_up(self):
        if len(self.completions) <= self.complete_amount:
            self.completion_num -= 1
            if self.completion_num == -1:
                self.completion_num = len(self.completions) - 1
        else:
            self.completion_num -= 1
            if self.completion_num < 0:
                self.completion_num = 0
                self.offset -= 1
                if self.offset < 0:
                    self.offset = len(self.completions) - self.complete_amount
                    self.completion_num = self.complete_amount - 1

    def go_down(self):
        self.completion_num += 1
        if self.completion_num >= min(self.complete_amount, len(self.completions)):
            self.completion_num -= 1
            self.offset += 1
            if self.offset + self.complete_amount > len(self.completions):
                self.offset = 0
                self.completion_num = 0

    def on_event(self, event: arcade.gui.UIEvent) -> bool | None:
        if isinstance(event, UITextMotionEvent):
            if event.motion in (arcade.key.UP, arcade.key.DOWN):
                if event.motion == arcade.key.DOWN:
                    self.go_down()
                elif event.motion == arcade.key.UP:
                    self.go_up()

                self.update()
                return EVENT_HANDLED

    def update(self):
        self.clear()
        children, y = self.get_children()
        self.height = y
        self.width = max(child.content_width for child in children) + self.pad * 2

        for child in children:
            self.add(child)

    @property
    def selected(self):
        return self.completions[self.offset + self.completion_num]


class BetterTextArea(arcade.gui.UITextArea):
    def __init__(self, *args, multiline: bool = True, **kwargs):
        super().__init__(*args, multiline=multiline, **kwargs)
        import pyglet
        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.doc,
            width=int(self.content_width),
            height=int(self.content_height),
            multiline=multiline,
        )


class CustomInputText(arcade.gui.UIInputText):
    delimiters = " /\\()\"'-.,:;<>~!@#$%^&*|+=[]{}~?│"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shift_held: bool = False

    def check_shift(self, event: UIKeyPressEvent | UIKeyReleaseEvent):
        if event.modifiers & arcade.key.MOD_SHIFT:
            self.shift_held = True
        else:
            self.shift_held = False

    def on_event(self, event: UIEvent) -> bool | None:
        if isinstance(event, UIKeyReleaseEvent):
            self.check_shift(event)

        if isinstance(event, UIKeyPressEvent):
            self.check_shift(event)

            ctrl_held = event.modifiers & arcade.key.MOD_CTRL

            if self.layout.multiline and event.symbol == arcade.key.ENTER and self.shift_held:
                old_text = self.text
                self.caret.on_text("\r")
                self.trigger_full_render()

                self.dispatch_event("on_change", UIOnChangeEvent(self, old_text, self.text))

                return EVENT_HANDLED
            elif event.symbol == arcade.key.A and ctrl_held:
                self.caret.select_all()
                return EVENT_HANDLED
            elif event.symbol == arcade.key.BACKSPACE and ctrl_held:
                caret = self.caret
                old_text = self.text
                if caret.mark is not None:
                    caret._delete_selection()
                    self.dispatch_event("on_change", UIOnChangeEvent(self, old_text, self.text))
                    return EVENT_HANDLED

                pos = caret.position - 1
                if pos >= 0 and self.text[pos] == " ":
                    caret._layout.document.delete_text(pos + 1, caret.position)
                    pos -= 1

                if pos >= 0:
                    char = self.text[pos]
                    if char in self.delimiters:
                        while pos > -1 and char in self.delimiters:
                            pos -= 1
                            char = self.text[pos]
                    else:
                        while pos > -1 and char not in self.delimiters:
                            pos -= 1
                            char = self.text[pos]

                    caret._layout.document.delete_text(pos + 1, caret.position)
                    caret._update()
                    caret.position = pos + 1
                    self.dispatch_event("on_change", UIOnChangeEvent(self, old_text, self.text))
                    return EVENT_HANDLED

                return EVENT_UNHANDLED
            elif pyperclip and event.symbol == arcade.key.V and ctrl_held:
                caret = self.caret
                if caret.mark is not None:
                    caret._delete_selection()

                position = caret.position

                pasted_text = pyperclip.paste()
                if not self.layout.multiline:
                    pasted_text = pasted_text.replace("\r", "").replace("\n", "")

                self.text = self.text[:caret.position] + pasted_text + self.text[caret.position:]
                caret.position = position + len(pasted_text)
                return EVENT_HANDLED
            elif pyperclip and event.symbol in (arcade.key.C, arcade.key.X) and ctrl_held and self.caret.mark is not None:
                caret = self.caret
                if caret.mark is None:
                    return EVENT_UNHANDLED

                start = min(caret.position, caret.mark)
                end = max(caret.position, caret.mark)

                pyperclip.copy(self.text[start:end])

                if event.symbol == arcade.key.X:
                    old_text = self.text
                    caret._delete_selection()
                    self.dispatch_event("on_change", UIOnChangeEvent(self, old_text, self.text))

                return EVENT_HANDLED

        if isinstance(event, UITextEvent):
            if isinstance(event, UITextInputEvent) and event.text == "\r":
                if (self.layout.multiline and self.shift_held is False) or not self.layout.multiline:
                    self.dispatch_event("on_summit")
                    return EVENT_HANDLED

        return super().on_event(event)

    def on_summit(self) -> None:
        """Event triggered when the input text is submitted.

        @input_text.event("on_summit")
        def _():
            print(f"Summit: {input_text.text}")
            # here we can handle the input text, e.g. send it to a server or process it
        """


CustomInputText.register_event_type("on_summit")


class CommandView(arcade.gui.UIView):
    history: list[str] = []
    history_index = -1

    def __init__(
        self,
        background_view: arcade.View | arcade.Window,
        font: str | Sequence[str] = ("Arial", ),
        font_size: int = 20,
    ):
        self.background_view = background_view
        super().__init__()
        self.background_color = background_view.background_color or arcade.color.WHITE

        self.default_attributes = {
            "font_name": font,
            "font_size": font_size,
            "italic": False,
            "underline": None,
            "kerning": 0,
            "baseline": 0,
            "color": (255, 255, 255, 255),
            "background_color": None
        }

        self.grid = self.ui.add(
            arcade.gui.UIGridLayout(
                size_hint=(1, 1),
                column_count=1,
                row_count=2
            )
        )
        self.grid.with_background(color=Color(0, 0, 0, 110))

        pg_font = pyglet.font.load(font, size=font_size)
        self.input_text_height = pg_font.get_text_size("/Help")[1] + 10
        # self.input_text_height = input_text_height

        height = background_view.height
        input_height = self.input_text_height / height
        text_area_height = 1 - input_height

        self.text_area = self.grid.add(
            BetterTextArea(
                text="<br>" * 50,
                text_color=(255, 255, 255, 255),
                size_hint=(1, text_area_height),
                font_name=font,
                font_size=font_size,
                document_mode="HTML"  # allows for cool text.
            ),
            row=0
        )
        self.text_area.with_padding(left=8)
        self.text_area.trigger_full_render()
        self.text_area.top = height

        style = arcade.gui.UIInputText.UIStyle(bg=Color(0, 0, 0, 220), border=Color(0, 0, 0, 0), border_width=0)

        self.input_area = self.grid.add(
            CustomInputText(
                font=font,
                font_size=font_size,
                size_hint=(1, input_height),
                multiline=False,
                style={
                    "normal": style,
                    "hover": style,
                    "press": style,
                    "disabled": style,
                    "invalid": style,
                }
            ),
            row=1
        )
        self.input_area.with_padding(all=5)

        self.auto_complete: AutoComplete | None = None

        # self.suggestion = self.ui.add(
        #     UILabel(
        #         x=0,
        #         y=self.input_area.center_y - pg_font.get_text_size("Test")[1] // 2,
        #         font_name=font,
        #         font_size=font_size,
        #         text_color=(100, 100, 100),
        #         # italic=True
        #     )
        # )

        # i = 0
        # def a(dt):
        #     nonlocal i
        #     i += 1
        #     self.send_text(f"Hello {i}\n")
        # arcade.schedule(a, 1)

        @self.input_area.event("on_event")
        def _(event: arcade.gui.UIEvent):
            if self.auto_complete is None:
                # self.suggestion.text = ""
                return EVENT_UNHANDLED

            if isinstance(event, arcade.gui.UIKeyPressEvent) and event.symbol == arcade.key.TAB:
                input_area = self.input_area

                if input_area.text[self.auto_complete.index:] == self.auto_complete.selected:
                    if event.modifiers & arcade.key.MOD_SHIFT:
                        self.auto_complete.go_up()
                    else:
                        self.auto_complete.go_down()
                    self.auto_complete.update()

                new_text = input_area.text[:self.auto_complete.index] + self.auto_complete.selected
                input_area.doc.text = new_text
                if input_area._bg_color or input_area._bg_tex:
                    input_area.trigger_render()
                else:
                    input_area.trigger_full_render()

                self.input_area.caret.position = len(self.input_area.text)
                return EVENT_HANDLED

        @self.input_area.event("on_change")
        def _(event: arcade.gui.UIOnChangeEvent):
            source: arcade.gui.UIInputText = event.source
            height = source.layout.content_height + source.padding[0] + source.padding[2]
            source.resize(height=height, anchor=arcade.types.AnchorPoint.BOTTOM_CENTER)

            source.size_hint = (1, height / background_view.height)
            self.text_area.size_hint = (1, 1 - source.size_hint[1])
            self.text_area.bottom = source.top
            source.bottom = 0

            if not source.text.startswith("/"):
                if self.auto_complete:
                    self.ui.remove(self.auto_complete)
                    self.auto_complete = None
                return

            index, completions = self.get_completions(source.text)
            width = pg_font.get_text_size(source.text[:index])[0]

            if completions:
                if self.auto_complete is None:
                    self.auto_complete = self.ui.add(
                        AutoComplete(
                            x=width,
                            y=height + 5,
                            completions=completions,
                            index=index
                        )
                    )
                else:
                    self.auto_complete.left = width
                    self.auto_complete.bottom = height + 5
                    self.auto_complete.completions = completions
                    self.auto_complete.offset = 0
                    self.auto_complete.completion_num = 0
                    self.auto_complete.update()
            else:
                if self.auto_complete:
                    self.ui.remove(self.auto_complete)
                    self.auto_complete = None

            if self.auto_complete:
                self.auto_complete.left = width
                self.auto_complete.bottom = height + 5

            #     if source.text[self.auto_complete.index:] != self.auto_complete.selected:
            #         text = source.text[self.auto_complete.index:]
            #         remaining_text = self.auto_complete.selected[len(text):]
            #         self.suggestion.text = remaining_text
            #         self.suggestion.left = pg_font.get_text_size(source.text)[0] + 5
            # else:
            #     self.suggestion.text = ""

            return EVENT_HANDLED

        @self.input_area.event("on_summit")
        def _():
            text = self.input_area.text
            if not text:
                return

            self.history.append(text)

            if text == "/":
                return

            self.input_area.text = ""
            if text[0] == "/":  # the prefix is /
                try:
                    process_commands(
                        text[1:],
                        context=CommandContext(
                            self.window,
                            command_view=self
                        ),
                    )
                except Exception as e:
                    self.on_error(e)

    def on_error(self, error: Exception):
        pass

    def on_show_view(self):
        def _(dt):
            self.input_area.activate()
        arcade.schedule_once(_, .1)
        return super().on_show_view()

    def on_hide_view(self):
        self.input_area.deactivate()
        return super().on_hide_view()

    def send_text(self, text: str, **kwargs):
        """Append text to the text area."""
        start = len(self.text_area.text)

        for key, value in self.default_attributes.items():
            kwargs.setdefault(key, value)

        self.text_area.doc.insert_text(
            start,  # type: ignore
            text,
            attributes=kwargs,
        )

        self.text_area.layout.view_y = float("-inf")  # type: ignore
        self.text_area.trigger_full_render()

    def on_resize(self, width: int, height: int) -> bool | None:
        height = height
        input_height = self.input_text_height / height
        text_area_height = 1 - input_height

        self.text_area.size_hint = (width, text_area_height)
        self.input_area.size_hint = (width, input_height)

        self.input_area.bottom = 0
        self.text_area.top = height

    @property
    def text(self):
        return self.text_area.text

    @text.setter
    def text(self, value):
        self.text_area.text = value
        self.text_area.layout.view_y = float("inf") # type: ignore
        self.text_area.trigger_full_render()

    def get_completions(self, text: str) -> tuple[int, list[str]]:
        if not text:
            return -1, []

        try:
            if text == "/":
                return 1, [cmd.names[0] for cmd in get_command_list()]
        except IndexError:
            return -1, []

        if text[-1] == " ":
            return -1, []

        view = StringView(text.lstrip("/"))

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
        pos = 0
        if command:
            for child in command.children:
                for name in child.names:
                    if name.startswith(last_arg):
                        completions.append(name)

            with suppress(IndexError):
                for param in command.parameters[command.pass_context:]:
                    if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                        last_arg = view.get_next_word()
                    elif param.kind == inspect.Parameter.KEYWORD_ONLY:
                        last_arg = view.get_rest()
                        if not last_arg:
                            continue

                    pos = len(last_arg)

                    completions = param.get_completions(last_arg)
                    if (inspect.isclass(param.annotation) and issubclass(param.annotation, FlagConverter)) or isinstance(param.annotation, FlagConverter):
                        flag_conv = param.annotation
                        prefix = flag_conv._prefix or " "  # type: ignore
                        delimiter = flag_conv._delimiter  # type: ignore

                        flags = last_arg.split(prefix)
                        latest_flag = flags[-1]
                        if delimiter in latest_flag:
                            _, _, value = latest_flag.partition(delimiter)
                            pos = len(value)
                        else:
                            pos = len(latest_flag)
        elif command_list:
            pos = len(last_arg)
            completions = [name for command in command_list for name in command.names if name.startswith(last_arg)]

        return len(text) - pos, completions

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.ESCAPE:
            if self.auto_complete:
                self.ui.remove(self.auto_complete)
                self.auto_complete = None
            else:
                if isinstance(self.background_view, arcade.Window):
                    self.background_view.hide_view()
                    self.clear()
                else:
                    self.window.show_view(self.background_view)
        # elif self.auto_complete is None and symbol in (arcade.key.UP, arcade.key.DOWN):
        #     if symbol == arcade.key.UP:
        #         self.history_index = max(-1, self.history_index - 1)
        #     else:
        #         self.history_index = min(len(self.history) - 1, self.history_index + 1)

        #     if self.history_index == -1:
        #         self.input_area.text = ""
        #     else:
        #         self.input_area.text = self.history[self.history_index]

    def on_update(self, delta_time: float) -> bool | None:
        return self.background_view.on_update(delta_time)

    def on_draw_before_ui(self) -> bool | None:
        return self.background_view.on_draw()
