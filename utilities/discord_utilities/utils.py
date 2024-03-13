import discord
import typing
from discord.ext import commands


def get_image_url(
        context_or_interaction: typing.Union[discord.Interaction, commands.Context], string: typing.Optional[str]
        ):
    if string.lower() in ["user", "author"]:
        if isinstance(context_or_interaction, discord.Interaction):
            user = context_or_interaction.user
        else:
            user = context_or_interaction.author

        return user.display_avatar.url
    elif string.lower() in ["guild", "server"] and context_or_interaction.guild:
        guild = context_or_interaction.guild
        if guild.icon:
            return guild.icon.url
        else:
            return None
    elif string.isdigit():
        return None  # WIP

    return string
