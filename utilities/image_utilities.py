import numpy as np
from PIL import Image

def get_avg_color(path):
    image = Image.open(path)
    image_array = np.array(image)
    average_color = np.mean(image_array, axis=(0, 1))
    r, g, b, _ = tuple(average_color.astype(int))
    return r, g, b
