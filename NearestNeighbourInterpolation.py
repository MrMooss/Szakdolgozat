from PIL import Image
import numpy as np
import cv2

def nearest_neighbor_interpolation(img_path):
    original_image = Image.open(img_path)
    original_width, original_height = original_image.size
    new_width = original_width * 4
    new_height = original_height * 4
    interpolated_image = Image.new("RGB", (new_width, new_height))
    for y in range(new_height):
        for x in range(new_width):
            source_x = int(x / 4.0)
            source_y = int(y / 4.0)
            source_x = min(original_width - 1, max(0, source_x))
            source_y = min(original_height - 1, max(0, source_y))
            pixel = original_image.getpixel((source_x, source_y))
            interpolated_image.putpixel((x, y), pixel)
    return interpolated_image
def nearest_interpolation(path):
    nearest_image = nearest_neighbor_interpolation(path)
    nearest_image = np.array(nearest_image)
    nearest_image = nearest_image[:, :, ::-1]
    cv2.imwrite("nearest.jpg", nearest_image)
    return nearest_image