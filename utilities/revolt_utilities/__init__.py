import revolt
from .paginator import Paginator, embed_creator


def convert_to_file(txt: str | bytes, filename: str):
    if isinstance(txt, str):
        return revolt.File(txt.encode('utf-8'), filename=filename)
    else:
        return revolt.File(txt, filename=filename)
