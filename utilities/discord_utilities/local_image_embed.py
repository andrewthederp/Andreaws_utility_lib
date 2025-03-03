import io
import random
import typing
from typing import Any, Optional

import discord
import discord.http
from discord.ext import commands

try:
    from PIL import Image
except ImportError:
    Image = None

if Image:
    type_hint = typing.Union[str, discord.File, Image.Image]
else:
    type_hint = typing.Union[str, discord.File]

MISSING = discord.utils.MISSING
original_embed_class = discord.Embed
original_handle_message_parameters_function = discord.http.handle_message_parameters
original_interaction_message_response_params_function = discord.async_.interaction_message_response_params


class LocalImageEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.files = []

    async def send(
            self,
            destination: typing.Union[discord.abc.Messageable, discord.Interaction, discord.Webhook],
            **kwargs
    ) -> typing.Union[discord.WebhookMessage, discord.Message, None]:
        files = kwargs.pop('files', [])
        self.files.extend(files)
        if isinstance(destination, discord.Interaction):
            await destination.response.send_message(embed=self, files=self.files, **kwargs)
        else:
            return await destination.send(embed=self, files=self.files, **kwargs)

    async def edit(
            self,
            editable: typing.Union[commands.Context, discord.Interaction, discord.Message, discord.Webhook],
            **kwargs
    ):
        files = kwargs.pop('files', [])
        self.files.extend(files)

        if isinstance(editable, discord.Interaction):
            await editable.response.edit_message(embed=self, attachments=self.files, **kwargs)
        elif isinstance(editable, discord.Webhook):
            message_id = kwargs.pop('message_id')
            await editable.edit_message(message_id, embed=self, attachments=self.files, **kwargs)
        else:
            editable: commands.Context | discord.Message
            await editable.edit(embed=self, attachments=self.files, **kwargs)

    def set_image(self, *, url: type_hint):
        if isinstance(url, str):
            super().set_image(url=url)
        elif isinstance(url, discord.File):
            super().set_image(url="attachment://" + url.filename)
            self.files.append(url)
        elif Image and isinstance(url, Image.Image):
            buffer = io.BytesIO()
            url.save(buffer, "PNG")
            buffer.seek(0)

            filename = ''.join(random.choice(list('abcdefghijklmnopqrstuvwxyz1234567890')) for _ in range(10)) + '.png'
            file = discord.File(buffer, filename=filename)
            self.files.append(file)

            super().set_image(url="attachment://" + file.filename)

        return self

    def set_thumbnail(self, *, url: type_hint):
        if isinstance(url, str):
            super().set_thumbnail(url=url)
        elif isinstance(url, discord.File):
            super().set_thumbnail(url="attachment://" + url.filename)
            self.files.append(url)
        elif Image and isinstance(url, Image.Image):
            buffer = io.BytesIO()
            url.save(buffer, "PNG")
            buffer.seek(0)

            filename = ''.join(random.choice(list('abcdefghijklmnopqrstuvwxyz1234567890')) for _ in range(10)) + '.png'
            file = discord.File(buffer, filename=filename)
            self.files.append(file)

            super().set_thumbnail(url="attachment://" + file.filename)

        return self

    def set_author(self, *, name: str, url: str | None = None, icon_url: type_hint | None = None):
        if isinstance(icon_url, str | None):
            super().set_author(name=name, url=url, icon_url=icon_url)
        elif isinstance(icon_url, discord.File):
            super().set_author(name=name, url=url, icon_url="attachment://" + icon_url.filename)
            self.files.append(icon_url)
        elif Image and isinstance(icon_url, Image.Image):
            buffer = io.BytesIO()
            icon_url.save(buffer, "PNG")
            buffer.seek(0)

            filename = ''.join(random.choice(list('abcdefghijklmnopqrstuvwxyz1234567890')) for _ in range(10)) + '.png'
            file = discord.File(buffer, filename=filename)
            self.files.append(file)

            super().set_author(name=name, url=url, icon_url="attachment://" + file.filename)

        return self

    def set_footer(self, *, text: str | None = None, icon_url: type_hint | None = None):
        if isinstance(icon_url, str | None):
            super().set_footer(text=text, icon_url=icon_url)
        elif isinstance(icon_url, discord.File):
            super().set_footer(text=text, icon_url="attachment://" + icon_url.filename)
            self.files.append(icon_url)
        elif Image and isinstance(icon_url, Image.Image):
            buffer = io.BytesIO()
            icon_url.save(buffer, "PNG")
            buffer.seek(0)

            filename = ''.join(random.choice(list('abcdefghijklmnopqrstuvwxyz1234567890')) for _ in range(10)) + '.png'
            file = discord.File(buffer, filename=filename)
            self.files.append(file)

            super().set_footer(text=text, icon_url="attachment://" + file.filename)

        return self


def make_embeds_support_local_images():
    discord.Embed = LocalImageEmbed

    def new_handle_message_parameters_function(*args, **kwargs):
        files = kwargs.pop("files", MISSING)
        embeds = kwargs.pop("embeds", MISSING)

        file = kwargs.pop("file", MISSING)
        embed = kwargs.pop("embed", MISSING)

        if embeds is not MISSING and embed is not MISSING:
            raise TypeError('Cannot mix embed and embeds keyword arguments.')
        if files is not MISSING and file is not MISSING:
            raise TypeError('Cannot mix file and files keyword arguments.')

        if files is discord.utils.MISSING:
            files = []
        if embeds is discord.utils.MISSING:
            embeds = []

        if file is not MISSING:
            files.append(file)

        if embed is not MISSING:
            # files.extend(embed.files)
            embeds.append(embed)

        for embed in embeds:
            files.extend(embed.files)

        return original_handle_message_parameters_function(*args, embeds=embeds if embeds else MISSING, files=files if files else MISSING, **kwargs)

    def new_interaction_message_response_params_function(*args, **kwargs):
        files = kwargs.pop("files", MISSING)
        embeds = kwargs.pop("embeds", MISSING)

        file = kwargs.pop("file", MISSING)
        embed = kwargs.pop("embed", MISSING)

        if embeds is not MISSING and embed is not MISSING:
            raise TypeError('Cannot mix embed and embeds keyword arguments.')
        if files is not MISSING and file is not MISSING:
            raise TypeError('Cannot mix file and files keyword arguments.')

        if files is discord.utils.MISSING:
            files = []
        if embeds is discord.utils.MISSING:
            embeds = []

        if file is not MISSING:
            files.append(file)

        if embed is not MISSING:
            # files.extend(embed.files)
            embeds.append(embed)

        for embed in embeds:
            files.extend(embed.files)

        return original_interaction_message_response_params_function(*args, embeds=embeds if embeds else MISSING, files=files if files else MISSING, **kwargs)

    discord.abc.handle_message_parameters = new_handle_message_parameters_function
    discord.channel.handle_message_parameters = new_handle_message_parameters_function
    discord.interactions.handle_message_parameters = new_handle_message_parameters_function
    discord.http.handle_message_parameters = new_handle_message_parameters_function
    discord.message.handle_message_parameters = new_handle_message_parameters_function
    discord.async_.handle_message_parameters = new_handle_message_parameters_function
    discord.sync.handle_message_parameters = new_handle_message_parameters_function

    discord.async_.interaction_message_response_params = new_interaction_message_response_params_function
    discord.interactions.interaction_message_response_params = new_interaction_message_response_params_function


def unmake_embeds_support_local_images():
    discord.Embed = original_embed_class

    discord.abc.handle_message_parameters = original_handle_message_parameters_function
    discord.channel.handle_message_parameters = original_handle_message_parameters_function
    discord.interactions.handle_message_parameters = original_handle_message_parameters_function
    discord.http.handle_message_parameters = original_handle_message_parameters_function
    discord.message.handle_message_parameters = original_handle_message_parameters_function
    discord.async_.handle_message_parameters = original_handle_message_parameters_function
    discord.sync.handle_message_parameters = original_handle_message_parameters_function

    discord.async_.interaction_message_response_params = original_interaction_message_response_params_function
    discord.interactions.interaction_message_response_params = original_interaction_message_response_params_function
