import numpy as np
from PIL import Image
import os
import cv2

def resizeImage(name):
    img1 = Image.open(name)

    old = np.asarray(img1)
    rows, cols, layers = old.shape
    new = np.zeros((2 * rows - 1, 2 * cols - 1, layers))

    for layer in range(3):
        new[:, :, layer] = resizeLayer(old[:, :, layer])

    new = new.astype(np.uint8)
    img2 = Image.fromarray(new)
    img2.save("linear.jpg")

    img1 = Image.open('linear.jpg')

    old = np.asarray(img1)
    rows, cols, layers = old.shape
    new = np.zeros((2 * rows - 1, 2 * cols - 1, layers))

    for layer in range(3):
        new[:, :, layer] = resizeLayer(old[:, :, layer])

    new = new.astype(np.uint8)
    img2 = Image.fromarray(new)

    cvImg = pil2cv(img2)

    img2 = cvImg

    os.remove("linear.jpg")
    cv2.imwrite("linearx2.jpg", img2)
    return img2

def pil2cv(image):
    mode = image.mode
    new_image: np.ndarray
    if mode == '1':
        new_image = np.array(image, dtype=np.uint8)
        new_image *= 255
    elif mode == 'L':
        new_image = np.array(image, dtype=np.uint8)
    elif mode == 'LA' or mode == 'La':
        new_image = np.array(image.convert('RGBA'), dtype=np.uint8)
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    elif mode == 'RGB':
        new_image = np.array(image, dtype=np.uint8)
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    elif mode == 'RGBA':
        new_image = np.array(image, dtype=np.uint8)
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    elif mode == 'LAB':
        new_image = np.array(image, dtype=np.uint8)
        new_image = cv2.cvtColor(new_image, cv2.COLOR_LAB2BGR)
    elif mode == 'HSV':
        new_image = np.array(image, dtype=np.uint8)
        new_image = cv2.cvtColor(new_image, cv2.COLOR_HSV2BGR)
    elif mode == 'YCbCr':
        # XXX: not sure if YCbCr == YCrCb
        new_image = np.array(image, dtype=np.uint8)
        new_image = cv2.cvtColor(new_image, cv2.COLOR_YCrCb2BGR)
    elif mode == 'P' or mode == 'CMYK':
        new_image = np.array(image.convert('RGB'), dtype=np.uint8)
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    elif mode == 'PA' or mode == 'Pa':
        new_image = np.array(image.convert('RGBA'), dtype=np.uint8)
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    else:
        raise ValueError(f'unhandled image color mode: {mode}')

    return new_image

def resizeLayer(old):
    rows, cols = old.shape

    rNew = 2 * rows - 1
    cNew = 2 * cols - 1
    new = np.zeros((rNew, cNew))

    new[0:rNew:2, 0:cNew:2] = old[0:rows, 0:cols]

    new[1:rNew:2, :] = (new[0:rNew - 1:2, :] + new[2:rNew:2, :]) / 2

    new[:, 1:cNew:2] = (new[:, 0:cNew - 1:2] + new[:, 2:cNew:2]) / 2

    new[1:rNew:2, 1:cNew:2] = (new[0:rNew - 2:2, 0:cNew - 2:2] +
                               new[0:rNew - 2:2, 2:cNew:2] +
                               new[2:rNew:2, 0:cNew - 2:2] +
                               new[2:rNew:2, 2:cNew:2]) / 4
    return new

def linear_interpolation(path):
    img = resizeImage(path)
    return img
