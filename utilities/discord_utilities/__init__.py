import io
import os
import re

import discord
from discord import app_commands
from discord.ext import commands

try:
    import jishaku
except ImportError:
    jishaku = None

from .embed_creator import EmbedCreator
from .confirmation import Confirm
from .modal_creator import MakeModal
from .local_image_embed import LocalImageEmbed, make_embeds_support_local_images, unmake_embeds_support_local_images
from .columned_view import ColumnedView, ColumnedButton, columned_button, make_views_columned, make_views_uncolumned
from .paginator import Paginator, PaginatorBehaviour, embed_creator
from .utils import get_image_url
from .toggle_button import ToggleButton


class MoneyConverter(commands.Converter):
    get_money = NotImplemented

    allow_negative: bool = False
    allow_zero: bool = False

    def __init__(self, *, allow_negative: bool = False, allow_zero: bool = False):
        self.allow_negative = allow_negative
        self.allow_zero = allow_zero

    async def convert(self, ctx: commands.Context, original_amount: str) -> int | float:
        amount = original_amount.lower()
        if self.get_money is not NotImplemented:
            max_amount = await discord.utils.maybe_coroutine(self.get_money, ctx)
            amount = amount.replace("max", f"{max_amount}")
            amount = amount.replace("all", f"{max_amount}")
            amount = amount.replace("half", f"{max_amount // 2}")

        amount = re.sub(r"[^0-9ek.]", "", amount)
        amount = amount.replace("k", "000")
        amount = amount.replace("e", "*10**")
        try:
            if amount == 0 and not self.allow_zero:
                raise commands.BadArgument(f"{original_amount} must be a positive number")

            if amount < 0 and not self.allow_negative:
                raise commands.BadArgument(f"{original_amount} must be a positive number{' or zero' if self.allow_zero else ''}")

            amount = eval(amount)  # I don't think a code injection should be possible but remain wary /shrug
            return int(amount) if amount == int(amount) else amount  # convert from float to int if the value will remain unchanged
        except:
            raise commands.BadArgument(f"{original_amount} could not be converted into an integer")


class MoneyTransformer(app_commands.Transformer):
    get_money = NotImplemented

    allow_negative: bool = False
    allow_zero: bool = False

    def __init__(self, *, allow_negative: bool = False, allow_zero: bool = False):
        self.allow_negative = allow_negative
        self.allow_zero = allow_zero

    async def transform(self, interaction: discord.Interaction, original_amount: str) -> int | float:
        amount = original_amount.lower()
        if self.get_money is not NotImplemented:
            max_amount = await discord.utils.maybe_coroutine(self.get_money, interaction)
            amount = amount.replace("max", f"{max_amount}")
            amount = amount.replace("all", f"{max_amount}")
            amount = amount.replace("half", f"{max_amount // 2}")

        amount = re.sub(r"[^0-9ek.]", "", amount)
        amount = amount.replace("k", "000")
        amount = amount.replace("e", "*10**")
        try:
            if amount == 0 and not self.allow_zero:
                raise app_commands.TransformerError(original_amount, discord.AppCommandOptionType.string, self)

            if amount < 0 and not self.allow_negative:
                raise app_commands.TransformerError(original_amount, discord.AppCommandOptionType.string, self)

            amount = eval(amount)  # I don't think a code injection should be possible but remain wary /shrug
            return int(amount) if amount == int(amount) else amount  # convert from float to int if the value will remain unchanged
        except:
            raise app_commands.TransformerError(original_amount, discord.AppCommandOptionType.string, self)


class PartialMember(discord.Member):
    def __init__(self, *, guild: discord.Guild, member_id: int):
        self.guild = guild
        self.id = member_id


def convert_to_file(txt: str | bytes, filename: str) -> discord.File:
    if isinstance(txt, str):
        return discord.File(io.BytesIO(txt.encode('utf-8')), filename=filename)
    else:
        return discord.File(io.BytesIO(txt), filename=filename)


async def load_extensions(bot, path_to_extensions, *, func=lambda i: None) -> None:
    for ext in os.listdir(path_to_extensions):
        if ext.endswith(".py"):
            await bot.load_extension(f"{path_to_extensions.replace('/', '.')}.{ext[:-3]}")
            func(ext)


async def can_dm(user: discord.Member | discord.User) -> bool:
    try:
        await user.send()
    except discord.Forbidden:
        return False
    except discord.HTTPException:
        return True
    else:
        return True


if jishaku:
    def set_preferred_jishaku_flags():
        os.environ.setdefault("JISHAKU_NO_UNDERSCORE", "1")
        os.environ.setdefault("JISHAKU_FORCE_PAGINATOR", "1")
        os.environ.setdefault("JISHAKU_NO_DM_TRACEBACK", "1")
        os.environ.setdefault("JISHAKU_HIDE", "1")
        os.environ.setdefault("JISHAKU_USE_ANSI_ALWAYS", "1")
        os.environ.setdefault("JISHAKU_USE_ANSI_NEVER", "1")
else:
    set_preferred_jishaku_flags = NotImplemented
