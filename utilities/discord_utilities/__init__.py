import discord

import os

try:
    import jishaku
except ImportError:
    jishaku = None

from .embed_creator import EmbedCreator
from .confirmation import Confirm
from .modal_creator import MakeModal
from .local_image_embed import LocalImageEmbed
from .columned_view import ColumnedView, ColumnedButton, columned_button, make_views_columned, make_views_uncolumned
from .paginator import Paginator, PaginatorBehaviour, embed_creator
from .utils import get_image_url


def convert_to_file(txt: str | bytes, filename: str):
    import io
    if isinstance(txt, str):
        return discord.File(io.BytesIO(txt.encode('utf-8')), filename=filename)
    else:
        return discord.File(io.BytesIO(txt), filename=filename)


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

    # amount = amount.replace("max", f"{max_amt}")
    # amount = amount.replace("all", f"{max_amt}")
    # amount = re.sub(r"[^0-9ekEK.]", r"", amount)
    # amount = amount.replace(".0", "")
    # amount = amount.replace("k", "*1000")
    # amount = amount.replace("e", "*10**")
