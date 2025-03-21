from PIL import ImageFont, Image

try:
    import numpy as np  # type: ignore
except ImportError:
    np = None


class ResizeableTrueTypeFont:
    def __init__(self, font_path):
        self.font_path = font_path

    def __getitem__(self, size):
        return ImageFont.truetype(self.font_path, size)


if np:
    def get_avg_color(path):
        image = Image.open(path)
        image_array = np.array(image)
        average_color = np.mean(image_array, axis=(0, 1))
        r, g, b, _ = tuple(average_color.astype(int))
        return r, g, b
else:
    get_avg_color = NotImplemented
