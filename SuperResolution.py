import glob

import GAN
import os
import cv2
import numpy as np
from keras.models import load_model
import ImageSplitAndMerge as ism
from PIL import Image, ImageQt
import tempfile
import shutil

generator = load_model('best_gene_720_loss_2.26_ep.h5', compile=False)


def generateHrOld(img):
    with tempfile.TemporaryDirectory() as temp:
        #img = Image.open(path)
        h, w = img.size
        if h != 32 or w != 32:
            img = ism.expand_image(img)
            x, y = ism.crop(temp, img)
            images = glob.glob(temp + '/bg_*.jpg')
            for im in images:
                img2 = convertImage(im)
                hr = generator.predict(img2)
                hr = cv2.convertScaleAbs(hr, alpha=(255.0))
                cv2.imwrite(temp + '/' + os.path.basename(im), hr[0, :, :, ::-1])
            imagehigh = ism.merge_images(temp, y, x)
            imagehigh = imagehigh[0:w*4, 0:h*4]
            return imagehigh
        else:
            #img = convertImage(path)
            highres = generator.predict(img)
            highres = cv2.convertScaleAbs(highres, alpha=(255.0))
            cv2.imwrite(temp + '/test.jpg', highres[0, :, :, ::-1])
            test = cv2.imread(temp + '/test.jpg')
            return test


def generateHr(path):
    with tempfile.TemporaryDirectory() as temp:
        img = Image.open(path)
        h, w = img.size
        scale_factor = 4  # Assuming you want to upscale the image by a factor of 4
        stride = 30 # Set the desired stride for overlapping windows

        if h != 32 or w != 32:
            img = ism.expand_image(img)
            patches, x, y = ism.sliding_window(temp, img, stride)

            for patch in patches:
                img2 = convertImage(patch)
                hr = generator.predict(img2)
                hr = cv2.convertScaleAbs(hr, alpha=(255.0))
                cv2.imwrite(os.path.join(temp, f'{os.path.basename(patch)}'), hr[0, :, :, ::-1])

            imagehigh = ism.merge_patches(temp, scale_factor, x, y, generateHrOld(img))
            imagehigh = imagehigh[0:w * scale_factor, 0:h * scale_factor]

            return imagehigh
        else:
            img = convertImage(path)
            highres = generator.predict(img)
            highres = cv2.convertScaleAbs(highres, alpha=(255.0))
            cv2.imwrite(os.path.join(temp, 'patch_test.jpg'), highres[0, :, :, ::-1])
            test = cv2.imread(os.path.join(temp, 'patch_test.jpg'))
            return test



def convertImage(path):
    lr_img = cv2.imread(path)
    lr_img = cv2.cvtColor(lr_img, cv2.COLOR_BGR2RGB)
    lr_img = lr_img / 255
    lr_img = np.expand_dims(lr_img, axis=0)
    return lr_img


# SUPER RESOLUTION PADDING WITH IMAGE THEN OVERLAP