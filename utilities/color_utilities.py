import re

class Color:
    def __init__(self, r: int, g: int, b: int, *, a: int = 255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def __str__(self):
        return f"0x{self.r:02x}{self.g:02x}{self.b:02x}"

    def __int__(self):
        return (self.r << 16) | (self.g << 8) | self.b

    def __getitem__(self, indice):
        return self.rgba[indice]

    def get_luminance(self):
        return 0.299 * self.r + 0.587 * self.g + 0.114 * self.b

    def get_saturation(self):
        r, g, b = self.rgb
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        if r == g == b:
            return 0

        return (max_c - min_c) / max_c

    @property
    def decimal(self):
        return int(self)

    @property
    def rgba(self):
        return (self.r, self.g, self.b, self.a)

    @property
    def rgb(self):
        return (self.r, self.g, self.b)

    @property
    def hex(self):
        return str(self)

    @property
    def uniform(self):
        return (self.r / 255, self.g / 255, self.b / 255, self.a / 255)

    @classmethod
    def from_hex(cls, hex_value: int):
        return cls.from_int(hex_value)

    @classmethod
    def from_rgb(cls, r, g, b):
        return cls(r, g, b)

    @classmethod
    def from_rgba(cls, r, g, b, *, a=255):
        return cls(r, g, b, a=a)

    @classmethod
    def from_int(cls, decimal: int):
        return cls((decimal >> 16) & 0xFF, (decimal >> 8) & 0xFF, decimal & 0xFF)

    @classmethod
    def from_str(cls, value: str):
        if value.startswith("#"):
            value = value[1:]
        elif value.startswith("0x"):
            value = value[2:]

        try:
            return cls.from_int(int(value, base=16))
        except ValueError:
            pass

        match = re.match(r"(rgb)?\((?P<red>\d{1,3}),( )?(?P<green>\d{1,3}),( )?(?P<blue>\d{1,3})(,( )?(?P<alpha>\d{1,3}))?\)", value)  # rgb match
        if match:
            r = int(match["red"])
            g = int(match["green"])
            b = int(match["blue"])
            a = int(match["alpha"] or 255)
            if any(x not in range(256) for x in (r, g, b, a)):
                raise

            return cls(r, g, b, a=a)
        raise
