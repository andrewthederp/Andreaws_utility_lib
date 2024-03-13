import discord

from .embed_creator import EmbedCreator
from .confirmation import Confirm
from .modal_creator import MakeModal
from .local_image_embed import LocalImageEmbed
from .columned_view import ColumnedView, ColumnedButton, make_views_columned, columned_button
from .paginator import Paginator, PaginatorBehaviour, embed_creator
from .utils import get_image_url


def convert_to_file(txt: str | bytes, filename: str):
    import io
    if isinstance(txt, str):
        return discord.File(io.BytesIO(txt.encode('utf-8')), filename=filename)
    else:
        return discord.File(io.BytesIO(txt), filename=filename)

    # amount = amount.replace("max", f"{max_amt}")
    # amount = amount.replace("all", f"{max_amt}")
    # amount = re.sub(r"[^0-9ekEK.]", r"", amount)
    # amount = amount.replace(".0", "")
    # amount = amount.replace("k", "*1000")
    # amount = amount.replace("e", "*10**")
