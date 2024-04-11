from typing import Any

import discord
from discord import Interaction
from discord._types import ClientT
from discord.ext import commands
from .modal_creator import MakeModal
import typing
from enum import Enum


class PaginatorBehaviour:
    loop_around = 0
    disallow = 1
    disable = 2


class DisablePaginator(discord.ui.Button["Paginator"]):
    def __init__(self, label, style, row, emoji):
        super().__init__(label=label, style=style, row=row, emoji=emoji)

    async def callback(self, interaction):
        view = self.view
        view.stop()
        for child in view.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)


class DeletePaginator(discord.ui.Button["Paginator"]):
    def __init__(self, label, style, row, emoji):
        super().__init__(label=label, style=style, row=row, emoji=emoji)

    async def callback(self, interaction):
        view = self.view
        view.stop()
        await interaction.response.defer()
        if view.message:
            try:
                await view.message.delete()
            except discord.NotFound:
                pass


class EndPaginator(discord.ui.Button["Paginator"]):
    def __init__(self, label, style, row, emoji):
        super().__init__(label=label, style=style, row=row, emoji=emoji)

    async def callback(self, interaction):
        view = self.view
        view.stop()
        await interaction.response.edit_message(view=None)


class FirstPage(discord.ui.Button["Paginator"]):
    def __init__(self, label, style, row, emoji):
        super().__init__(label=label, style=style, row=row, emoji=emoji)

    async def callback(self, interaction):
        view = self.view
        view.current_page = 0

        await view.before_callback(interaction)
        await view.edit_paginator(interaction)
        await view.after_callback(interaction)


class PreviousPage(discord.ui.Button["Paginator"]):
    def __init__(self, label, style, row, emoji):
        super().__init__(label=label, style=style, row=row, emoji=emoji)

    async def callback(self, interaction):
        view = self.view
        view.current_page -= 1
        if view.paginator_behaviour == PaginatorBehaviour.loop_around and view.current_page == -1:
            view.current_page = len(view.pages) - 1
        elif view.paginator_behaviour == PaginatorBehaviour.disallow and view.current_page == -1:
            view.current_page = 0
            return await interaction.response.send_message(content=f"You can't do that!", ephemeral=True)

        await view.before_callback(interaction)
        await view.edit_paginator(interaction)
        await view.after_callback(interaction)


class ShowPage(discord.ui.Button["Paginator"]):
    def __init__(self, style, row, emoji):
        super().__init__(label="1", style=style, row=row, emoji=emoji, disabled=True)


class GotoPage(discord.ui.Button["Paginator"]):
    def __init__(self, style, row, emoji):
        super().__init__(label="1", style=style, row=row, emoji=emoji)

    async def callback(self, interaction):
        view = self.view

        async def modal_callback(inter, values):
            page = values['page?']
            if not page.isdigit() or int(page)-1 not in range(len(view.pages)):
                return await inter.response.send_message(content="That's not a valid number!")
            else:
                view.current_page = int(page) - 1
                await view.before_callback(inter)
                await view.edit_paginator(inter)
                await view.after_callback(inter)

        await interaction.response.send_modal(MakeModal(title="Page number", callback=modal_callback, inputs=[discord.ui.TextInput(label="Page?", placeholder=f"Give a number between 1-{len(view.pages)}")]))


class NextPage(discord.ui.Button["Paginator"]):
    def __init__(self, label, style, row, emoji):
        super().__init__(label=label, style=style, row=row, emoji=emoji)

    async def callback(self, interaction):
        view = self.view
        view.current_page += 1
        if view.paginator_behaviour == PaginatorBehaviour.loop_around and view.current_page == len(view.pages):
            view.current_page = 0
        elif view.paginator_behaviour == PaginatorBehaviour.disallow and view.current_page == len(view.pages):
            view.current_page = len(view.pages) - 1
            return await interaction.response.send_message(content=f"You can't do that!", ephemeral=True)

        await view.before_callback(interaction)
        await view.edit_paginator(interaction)
        await view.after_callback(interaction)


class LastPage(discord.ui.Button["Paginator"]):
    def __init__(self, label, style, row, emoji):
        super().__init__(label=label, style=style, row=row, emoji=emoji)

    async def callback(self, interaction):
        view = self.view
        view.current_page = len(view.pages) - 1

        await view.before_callback(interaction)
        await view.edit_paginator(interaction)
        await view.after_callback(interaction)


class Paginator(discord.ui.View):
    def __init__(
            self,
            timeout: int = None,
            *,
            bot: commands.Bot,
            pages: typing.List[typing.Union[
                typing.Dict[str, typing.Union[discord.Embed, discord.File, str]], discord.Embed, discord.File, str]],
            paginator_behaviour: PaginatorBehaviour = 0
            ):
        super().__init__(timeout=timeout)

        self.bot = bot
        self.pages = pages
        self.paginator_behaviour = paginator_behaviour
        self.current_page = 0

        self.message = None

    async def on_timeout(self):
        self.stop()

    async def before_callback(self, interaction):
        pass

    async def after_callback(self, interaction):
        pass

    async def edit_paginator(self, interaction):
        for child in self.children:
            if isinstance(child, (ShowPage, GotoPage)):
                child.label = str(self.current_page + 1)
            elif isinstance(child, (PreviousPage, FirstPage)) and self.paginator_behaviour == PaginatorBehaviour.disable:
                if self.current_page == 0:
                    child.disabled = True
                else:
                    child.disabled = False
            elif isinstance(child, (NextPage, LastPage)) and self.paginator_behaviour == PaginatorBehaviour.disable:
                if self.current_page == len(self.pages) - 1:
                    child.disabled = True
                else:
                    child.disabled = False

        page = self.pages[self.current_page]
        if isinstance(page, dict):
            page['view'] = self
            await interaction.response.edit_message(**page)
        elif isinstance(page, discord.Embed):
            await interaction.response.edit_message(embed=page, view=self)
        elif isinstance(page, discord.File):
            await interaction.response.edit_message(attachments=[page], view=self)
        elif isinstance(page, str):
            await interaction.response.edit_message(content=page, view=self)

    async def start_paginator(self, destination: typing.Union[discord.Interaction, discord.abc.Messageable]) -> typing.Union[discord.Message, discord.InteractionMessage]:
        page = self.pages[self.current_page]

        dct = {}
        if isinstance(page, dict):
            dct = page
        elif isinstance(page, discord.Embed):
            dct['embed'] = page
        elif isinstance(page, discord.File):
            dct['file'] = page
        elif isinstance(page, str):
            dct['content'] = page

        dct["view"] = self

        if isinstance(destination, discord.Interaction):
            await destination.response.send_message(**dct)
            self.message = await destination.original_response()
        else:
            self.message = await destination.send(**dct)

        return self.message

    def add_button(
            self,
            action: typing.Literal["first", "previous", "show", "goto", "next", "last", "delete", "disable", "end"],
            *,
            label: typing.Optional[str] = None,
            style: discord.ButtonStyle = discord.ButtonStyle.secondary,
            row: typing.Optional[int] = None,
            emoji: typing.Optional[typing.Union[str, discord.Emoji, discord.PartialEmoji]] = None,
    ):
        button = None
        if action == "first":
            button = FirstPage(label, style, row, emoji)
            if self.paginator_behaviour == PaginatorBehaviour.disable and self.current_page == 0:
                button.disabled = True
            self.add_item(button)
        elif action == "previous":
            button = PreviousPage(label, style, row, emoji)
            if self.paginator_behaviour == PaginatorBehaviour.disable and self.current_page == 0:
                button.disabled = True
            self.add_item(button)
        elif action == "show":
            button = ShowPage(style, row, emoji)
            self.add_item(button)
        elif action == "goto":
            button = GotoPage(style, row, emoji)
            self.add_item(button)
        elif action == "next":
            button = NextPage(label, style, row, emoji)
            if self.paginator_behaviour == PaginatorBehaviour.disable and self.current_page == len(self.pages)-1:
                button.disabled = True
            self.add_item(button)
        elif action == "last":
            button = LastPage(label, style, row, emoji)
            if self.paginator_behaviour == PaginatorBehaviour.disable and self.current_page == len(self.pages)-1:
                button.disabled = True
            self.add_item(button)
        elif action == "delete":
            button = DeletePaginator(label, style, row, emoji)
            self.add_item(button)
        elif action == "disable":
            button = DisablePaginator(label, style, row, emoji)
            self.add_item(button)
        elif action == "end":
            button = EndPaginator(label, style, row, emoji)
            self.add_item(button)

        return button


def embed_creator(text, num, *, title='', prefix='', suffix='', color=None, colour=None):
    if color is not None and colour is not None:
        raise ValueError

    return [discord.Embed(title=title, description=prefix + (text[i:i + num]) + suffix,
                          color=color or colour) for i in range(0, len(text), num)]

