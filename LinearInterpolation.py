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
    cvImg = np.array(img2)
    img2 = cvImg
    os.remove("linear.jpg")
    cv2.imwrite("linearx2.jpg", img2)
    return img2
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

