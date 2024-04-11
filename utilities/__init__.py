try:
    import discord
    from .discord_utilities import *
except ImportError:
    pass

try:
    import revolt
    from .revolt_utilities import *
except ImportError:
    pass

try:
    from .image_utilities import *
except ImportError:
    pass

from .cli_utilities import *
from .color_utilities import *
from .math_utilities import *
from .misc import *
