import revolt
from revolt.ext import commands
import asyncio
import typing


async def first_page(paginator, _):
    paginator.current_page = 0


async def previous_page(paginator, _):
    paginator.current_page -= 1
    if paginator.current_page == -1:
        paginator.current_page = len(paginator.pages) - 1


async def goto_page(paginator, user):
    original_message = await paginator.message.channel.send(f"Enter page number (1-{len(paginator.pages)})")

    try:
        message = await paginator.client.wait_for('message', check=lambda m: m.author.id == user.id and paginator.message.channel == m.channel, timeout=20)
        try:
            await message.delete()
        except revolt.HTTPError:
            pass
    except asyncio.TimeoutError:
        await original_message.delete()
    else:
        await original_message.delete()
        content = message.content
        if not content.isdigit():
            error_message = await message.channel.send("Invalid page number.")
            await asyncio.sleep(3)
            await error_message.delete()
        else:
            page = int(content) - 1
            if page not in range(len(paginator.pages)):
                error_message = await message.channel.send("Invalid page number.")
                await asyncio.sleep(3)
                await error_message.delete()
            else:
                paginator.current_page = page


async def next_page(paginator, _):
    paginator.current_page += 1
    if paginator.current_page == len(paginator.pages):
        paginator.current_page = 0


async def last_page(paginator, _):
    paginator.current_page = len(paginator.pages) - 1


async def delete_page(paginator, _):
    await paginator.message.delete()
    return True


async def disable_page(paginator, _):
    await paginator.message.remove_all_reactions()
    return True


class Paginator:
    def __init__(
            self,
            timeout: int = None,
            *,
            client: revolt.Client,
            pages: typing.List[typing.Union[typing.Dict[
                str, typing.Union[revolt.SendableEmbed, revolt.File, str]], revolt.SendableEmbed, revolt.File, str]],
            ):
        self.timeout = timeout
        self.client = client
        self.pages = pages
        self.current_page = 0

        self.buttons = {}

        self.message = None

    async def before_callback(self):
        pass

    async def after_callback(self):
        pass

    async def edit_paginator(self):
        page = self.pages[self.current_page]
        if isinstance(page, dict):
            await self.message.edit(**kwargs)
        elif isinstance(page, revolt.SendableEmbed):
            await self.message.edit(embeds=[page])
        # elif isinstance(page, revolt.File):
        #     await self.message.edit(attachments=[page])
        elif isinstance(page, str):
            await self.message.edit(content=page)

    async def start_paginator(self, destination: revolt.Messageable, check=None) -> revolt.Message:
        page = self.pages[self.current_page]

        dct = {}
        if isinstance(page, dict):
            dct = page
        elif isinstance(page, revolt.SendableEmbed):
            dct['embed'] = page
        elif isinstance(page, revolt.File):
            dct['attachments'] = [page]
        elif isinstance(page, str):
            dct['content'] = page

        interactions = revolt.MessageInteractions(reactions=list(self.buttons.keys()))
        self.message = await destination.send(**dct, interactions=interactions)
        # for emoji in self.buttons:
        #     await self.message.add_reaction(emoji)

        while True:
            try:
                message, user, reaction_id = await self.client.wait_for('reaction_add', timeout=self.timeout, check=check)
                if user == self.client.user:
                    continue

                function = self.buttons.get(reaction_id)
                if not function:
                    continue

                try:
                    await message.remove_reaction(reaction_id, user)
                except revolt.HTTPError:
                    pass

                await self.before_callback()
                do_break = await function(self, user)

                if do_break:
                    break
                else:
                    await self.edit_paginator()
                    await self.after_callback()
            except asyncio.TimeoutError:
                break

    def add_button(
            self,
            action: typing.Literal["first", "previous", "goto", "next", "last", "delete", "disable"],
            *,
            emoji: typing.Union[str, revolt.Emoji]
    ):
        emoji_id = getattr(emoji, 'id', emoji)
        if action == "first":
            self.buttons[emoji_id] = first_page
        elif action == "previous":
            self.buttons[emoji_id] = previous_page
        elif action == "goto":
            self.buttons[emoji_id] = goto_page
        elif action == "next":
            self.buttons[emoji_id] = next_page
        elif action == "last":
            self.buttons[emoji_id] = last_page
        elif action == "delete":
            self.buttons[emoji_id] = delete_page
        elif action == "disable":
            self.buttons[emoji_id] = disable_page

        return self


def embed_creator(text, num, *, title='', prefix='', suffix='', color=None, colour=None):
    if color is not None and colour is not None:
        raise ValueError

    return [revolt.SendableEmbed(title=title, description=prefix + (text[i:i + num]) + suffix, colour=color or colour)
            for i in range(0, len(text), num)]
