import discord
from discord import ButtonStyle
from typing import Optional, Union, Dict, List, TypeVar
from discord import Emoji, PartialEmoji
from itertools import groupby
import inspect


V = TypeVar('V', bound=typing.Union['View', 'ColumnedView'], covariant=True)

original_function = discord.ui.View.to_components


class ColumnedView(discord.ui.View):
    def to_components(self):
        def key(item: ColumnedButton) -> int:
            return item._rendered_row or 0

        children = sorted(self._children, key=key)
        components: List[Dict[str, Any]] = []
        for _, group in groupby(children, key=key):
            children = [item.to_component_dict() for item in sorted(group, key=lambda item: getattr(item, 'column', 6))]  # implement better column'ing
            if not children:
                continue

            components.append(
                {
                    'type': 1,
                    'components': children,
                }
            )

        return components


class ColumnedButton(discord.ui.Button[V]):
    def __init__(
            self,
            *,
            column: int,
            style: ButtonStyle = ButtonStyle.secondary,
            label: Optional[str] = None,
            disabled: bool = False,
            custom_id: Optional[str] = None,
            url: Optional[str] = None,
            emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
            row: Optional[int] = None,
    ):
        super().__init__(
            style=style,
            label=label,
            disabled=disabled,
            custom_id=custom_id,
            url=url,
            emoji=emoji,
            row=row,
        )
        self.column = column


def columned_button(
        *,
        column: int,
        label: Optional[str] = None,
        custom_id: Optional[str] = None,
        disabled: bool = False,
        style: ButtonStyle = ButtonStyle.secondary,
        emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
        row: Optional[int] = None,
):
    def decorator(func):
        if not inspect.iscoroutinefunction(func):
            raise TypeError('button function must be a coroutine function')

        func.__discord_ui_model_type__ = ColumnedButton
        func.__discord_ui_model_kwargs__ = {
            'column': column,
            'style': style,
            'custom_id': custom_id,
            'url': None,
            'disabled': disabled,
            'label': label,
            'emoji': emoji,
            'row': row,
        }
        return func

    return decorator


def make_views_columned():
    discord.ui.View.to_components = ColumnedView.to_components


def make_views_uncolumned():
    discord.ui.View.to_components = original_function

