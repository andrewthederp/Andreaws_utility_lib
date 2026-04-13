import discord
from discord import ButtonStyle

from typing import Optional


class MessageButton(discord.ui.Button):  # a button that only sends a single message
    def __init__(
            self,
            *,
            style: ButtonStyle = ButtonStyle.secondary,
            label: Optional[str] = None,
            disabled: bool = False,
            custom_id: Optional[str] = None,
            emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None,
            row: Optional[int] = None,
            id: Optional[int] = None,
            **kwargs
    ):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, emoji=emoji, row=row, id=id)
        self.kwargs = kwargs

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(**self.kwargs)


class ModalButton(discord.ui.Button):  # a button that only sends a modal
    def __init__(
            self,
            modal: discord.ui.Modal,
            *,
            style: ButtonStyle = ButtonStyle.secondary,
            label: Optional[str] = None,
            disabled: bool = False,
            custom_id: Optional[str] = None,
            emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None,
            row: Optional[int] = None,
            id: Optional[int] = None
    ):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, emoji=emoji, row=row, id=id)
        self.modal = modal

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(self.modal)


class ViewSwitchButton(discord.ui.Button):  # a button that edits the message to switch to a different view
    def __init__(
            self,
            view: discord.ui.View,
            *,
            style: ButtonStyle = ButtonStyle.secondary,
            label: Optional[str] = None,
            disabled: bool = False,
            custom_id: Optional[str] = None,
            emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None,
            row: Optional[int] = None,
            id: Optional[int] = None
    ):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, emoji=emoji, row=row, id=id)
        self._view = view

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=self._view)
