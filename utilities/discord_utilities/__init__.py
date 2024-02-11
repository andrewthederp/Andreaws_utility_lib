import discord

from .embed_creator import *
from .modal_creator import *
from .local_image_embed import *
from .utils import get_image_url


def convert_to_file(txt: str, filename: str):
    import io
    return discord.File(io.BytesIO(txt.encode('utf-8')), filename=filename)
