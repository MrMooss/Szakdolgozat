import numpy as np
from PIL import Image
import os
import cv2

def resizeLayer(old):
    rows, cols = old.shape
    rNew = 2 * rows
    cNew = 2 * cols
    new = np.zeros((rNew, cNew))

    # Copy original pixels to new image at appropriate positions
    new[0:rNew:2, 0:cNew:2] = old

    # Interpolate pixels horizontally
    for i in range(0, rNew, 2):
        for j in range(1, cNew - 1, 2):
            new[i, j] = (new[i, j - 1] + new[i, j + 1]) / 2

    # Interpolate pixels vertically
    for i in range(1, rNew - 1, 2):
        for j in range(cNew):
            new[i, j] = (new[i - 1, j] + new[i + 1, j]) / 2

    return new

def resizeImage(name):
    img1 = Image.open(name)
    old = np.asarray(img1)
    rows, cols, layers = old.shape

    # Adjusted new array size to (2 * rows, 2 * cols, layers)
    new = np.zeros((2 * rows, 2 * cols, layers))
    for layer in range(3):
        new[:, :, layer] = resizeLayer(old[:, :, layer])

    new = new.astype(np.uint8)
    img2 = Image.fromarray(new)
    img2.save("linearx2.jpg")

    return np.array(img2)

def linear_interpolation(path):
    img = cv2.imread(path)
    h, w, c = img.shape
    if h == w :
        img = resizeImage(path)
        return img
    else :
        fx = 4
        fy = 4
        resizedImg = cv2.resize(img, dsize=None, fx=fx, fy=fy, interpolation=cv2.INTER_LINEAR)
        cv2.imwrite("linearx2.jpg", resizedImg)
        return resizedImg

