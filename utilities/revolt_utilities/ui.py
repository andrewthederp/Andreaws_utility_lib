import asyncio

import revolt
import logging

_logger = logging.getLogger(__name__)
_client = None


class Interaction:
    def __init__(self, message, user):
        self.message = message
        self.user = user
        self.channel = message.channel
        self.client = _client

    async def send(self, *args, **kwargs):
        await self.channel.send(*args, **kwargs)

    async def edit(self, *args, **kwargs):
        await self.message.edit(*args, **kwargs)


class Button:
    def __init__(self, emoji: revolt.Emoji | str):
        self.emoji = emoji
        self.emoji_id = getattr(emoji, 'id', emoji)
        self.view = None

    def __repr__(self):
        return f"<Button emoji={self.emoji}>"

    async def callback(self, _):
        pass


class View:
    def __init__(self, *, timeout: None | float = None, client: revolt.Client | None = None):
        self.timeout = timeout
        self.children = []
        if not _client and not client:
            raise ValueError("No client provided")

        if client:
            set_client(client)

        self.client = _client

        self._stopped = False

    def __repr__(self):
        return f"<View timeout={self.timeout} children={len(self.children)}>"

    def stop(self):
        self._stopped = True

    def add_item(self, item: Button):
        item.view = self
        self.children.append(item)

    def remove_item(self, item: Button | str):
        if isinstance(item, Button):
            self.children.remove(item)
        else:
            for i, child in enumerate(self.children):
                if child.emoji_id == item:
                    self.children.pop(i)
                    break

    async def interaction_check(self, interaction):
        return True

    async def on_timeout(self):
        pass

    async def on_error(self, interaction, error, item):
        _logger.error('Ignoring exception in view %r for item %r', self, item, exc_info=error)

    async def _run_callback(self, interaction, child):
        try:
            if await self.interaction_check(interaction):
                await child.callback(interaction)
        except Exception as e:
            await self.on_error(interaction, e, button)

    async def send(self, dest, *args, **kwargs):
        kwargs['interactions'] = revolt.MessageInteractions(reactions=[i.emoji_id for i in self.children])
        main_message = await dest.send(*args, **kwargs)

        while not self._stopped:
            try:
                message, user, reaction_id = await self.client.wait_for('reaction_add', timeout=self.timeout, check=lambda m, _, __: m.id == main_message.id)
                interaction = Interaction(message, user)
                for child in self.children:
                    if child.emoji_id == reaction_id:
                        await asyncio.create_task(self._run_callback(interaction, child))
                        break
            except asyncio.TimeoutError:
                await self.on_timeout()
                break


def set_client(obj):
    global _client
    _client = obj
