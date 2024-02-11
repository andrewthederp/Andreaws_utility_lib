import io
from utilities import random
import typing

import discord
from PIL import Image


class LocalImageEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.files = []

    async def send(self, destination: typing.Union[discord.abc.Messageable, discord.Interaction], **kwargs):
        files = kwargs.get('files', [])
        self.files.extend(files)
        if isinstance(destination, discord.Interaction):
            await destination.response.send_message(embed=self, files=self.files, **kwargs)
        else:
            await destination.send(embed=self, files=self.files, **kwargs)

    def set_image(self, *, url: typing.Union[str, discord.File, Image.Image]):
        if type(url) == str:
            super().set_image(url=url)
        elif type(url) == discord.File:
            super().set_image(url="attachment://" + url.filename)
            self.files.append(url)
        elif isinstance(url, Image.Image):
            buffer = io.BytesIO()
            url.save(buffer, "PNG")
            buffer.seek(0)

            filename = ''.join(random.choice(list('abcdefghijklmnopqrstuvwxyz1234567890')) for _ in range(10)) + '.png'
            file = discord.File(buffer, filename=filename)
            self.files.append(file)

            super().set_image(url="attachment://" + file.filename)

        return self

    def set_thumbnail(self, *, url: typing.Union[str, discord.File, Image.Image]):
        if isinstance(url, str):
            super().set_thumbnail(url=url)
        elif isinstance(url, discord.File):
            super().set_thumbnail(url="attachment://" + url.filename)
            self.files.append(url)
        elif isinstance(url, Image.Image):
            buffer = io.BytesIO()
            url.save(buffer, "PNG")
            buffer.seek(0)

            filename = ''.join(random.choice(list('abcdefghijklmnopqrstuvwxyz1234567890')) for _ in range(10)) + '.png'
            file = discord.File(buffer, filename=filename)
            self.files.append(file)

            super().set_thumbnail(url="attachment://" + file.filename)

        return self
