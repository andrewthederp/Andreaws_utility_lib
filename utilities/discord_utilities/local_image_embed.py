import discord
import typing

class LocalImageEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.files = []

    async def send(self, destination, **kwargs):
        await destination.send(embed=self, files=self.files, **kwargs)


    def set_image(self, *, url: typing.Union[str, discord.File]):
        if type(url) == str:
            super().set_image(url=url)
        elif type(url) == discord.File:
            super().set_image(url="attachment://"+url.filename)
            self.files.append(url)


