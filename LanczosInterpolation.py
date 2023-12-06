from PIL import Image
import math
import cv2

def lanczos_kernel(x, a=3):
    if x == 0:
        return 1
    elif abs(x) < a:
        return a * (math.sin(math.pi * x) * math.sin(math.pi * x / a)) / (math.pi * math.pi * x * x)
    else:
        return 0
def interp(img_path):
    original_image = Image.open(img_path)
    img = cv2.imread(img_path)
    original_width, original_height = original_image.size
    new_width = original_width * 4
    new_height = original_height * 4
    interpolated_image = Image.new("RGB", (new_width, new_height))
    resizedLanczos = cv2.resize(img,
                                dsize=None, fx=4, fy=4, interpolation=cv2.INTER_LANCZOS4)
    return resizedLanczos
    for y in range(new_height):
        for x in range(new_width):
            source_x = x / 4.0
            source_y = y / 4.0
            r_sum, g_sum, b_sum, weight_sum = 0, 0, 0, 0
            for i in range(int(source_x) - 2, int(source_x) + 3):
                for j in range(int(source_y) - 2, int(source_y) + 3):
                    if 0 <= i < original_width and 0 <= j < original_height:
                        weight = lanczos_kernel(source_x - i) * lanczos_kernel(source_y - j)
                        pixel = original_image.getpixel((i, j))
                        r_sum += weight * pixel[0]
                        g_sum += weight * pixel[1]
                        b_sum += weight * pixel[2]
                        weight_sum += weight
            r = int(r_sum / weight_sum)
            g = int(g_sum / weight_sum)
            b = int(b_sum / weight_sum)
            interpolated_image.putpixel((x, y), (r, g, b))
    return interpolated_image
def lanczos_interpolation(path):
    lanczos_image = interp(path)
    cv2.imwrite("lanczos.jpg", lanczos_image)
    return lanczos_image
