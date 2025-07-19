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
