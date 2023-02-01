import glob

import GAN
import os
import cv2
import numpy as np
from keras.models import load_model
import matplotlib.image as pltim
import matplotlib.pyplot as plt
import ImageSplitAndMerge as ism
from PIL import Image, ImageQt
import tempfile
import shutil

generator = load_model('gen_e_20.h5', compile=False)


def generateHr(path):
    with tempfile.TemporaryDirectory() as temp:
        img = Image.open(path)
        h, w = img.size
        if h != 32 or w != 32:
            img = ism.expand_image(img)
            x, y = ism.crop(temp, img)
            images = glob.glob(temp + '/*.jpg')
            for im in images:
                img2 = convertImage(im)
                hr = generator.predict(img2)
                hr = cv2.convertScaleAbs(hr, alpha=(255.0))
                cv2.imwrite(temp + '/' + os.path.basename(im), hr[0, :, :, ::-1])
            imagehigh = ism.merge_images(temp, y, x)
            imagehigh = imagehigh.crop((0, 0, h*4, w*4))
            imagehigh.save(temp + '/highimg.jpg')
            imagehigh = cv2.imread(temp + '/highimg.jpg')
            return imagehigh
        else:
            img = convertImage(path)
            highres = generator.predict(img)
            highres = cv2.convertScaleAbs(highres, alpha=(255.0))
            cv2.imwrite(temp + '/test.jpg', highres[0, :, :, ::-1])
            test = cv2.imread(temp + '/test.jpg')
            return test


def convertImage(path):
    lr_img = cv2.imread(path)
    lr_img = cv2.cvtColor(lr_img, cv2.COLOR_BGR2RGB)
    lr_img = lr_img / 255
    lr_img = np.expand_dims(lr_img, axis=0)
    return lr_img


