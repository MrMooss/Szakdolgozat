import glob
import os
import cv2
import numpy as np
from keras.models import load_model
import ImageSplitAndMerge as ism
from PIL import Image, ImageQt
import tempfile
import shutil
from PyQt5.QtCore import QObject, pyqtSignal

class SuperResolutionGenerator(QObject):
    progressUpdated = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.generator = load_model('best_gene_720_loss_2.26_ep.h5', compile=False)

    def generateHr(self, path):
        with tempfile.TemporaryDirectory() as temp:
            img = Image.open(path)
            h, w = img.size
            scale_factor = 4
            stride = 30

            if h != 32 or w != 32:
                img = ism.expand_image(img)
                patches, x, y = ism.sliding_window(temp, img, stride)
                total_patches = len(patches)

                for i, patch in enumerate(patches):
                    img2 = self.convertImage(patch)
                    hr = self.generator.predict(img2)
                    hr = cv2.convertScaleAbs(hr, alpha=(255.0))
                    cv2.imwrite(os.path.join(temp, f'{os.path.basename(patch)}'), hr[0, :, :, ::-1])

                    progress = int((i + 1) / (total_patches * 2) * 100)  # Half progress for generateHr
                    self.progressUpdated.emit(progress)

                self.progressUpdated.emit(50)
                imagehigh = ism.merge_patches(temp, scale_factor, x, y, self.generateHrOld(img, total_patches))
                imagehigh = imagehigh[0:w * scale_factor, 0:h * scale_factor]
                return imagehigh
            else:
                img = self.convertImage(path)
                highres = self.generator.predict(img)
                highres = cv2.convertScaleAbs(highres, alpha=(255.0))
                cv2.imwrite(os.path.join(temp, 'patch_test.jpg'), highres[0, :, :, ::-1])
                test = cv2.imread(os.path.join(temp, 'patch_test.jpg'))
                self.progressUpdated.emit(50)
                return test

    def generateHrOld(self, img, total_patches):
        with tempfile.TemporaryDirectory() as temp:
            h, w = img.size
            if h != 32 or w != 32:
                img = ism.expand_image(img)
                x, y = ism.crop(temp, img)
                images = glob.glob(temp + '/bg_*.jpg')
                for i, im in enumerate(images):
                    img2 = self.convertImage(im)
                    hr = self.generator.predict(img2)
                    hr = cv2.convertScaleAbs(hr, alpha=(255.0))
                    cv2.imwrite(temp + '/' + os.path.basename(im), hr[0, :, :, ::-1])

                    progress = int(50 + (i + 1) / (len(images) + total_patches) * 50)  # Remaining progress for generateHrOld
                    self.progressUpdated.emit(progress)

                imagehigh = ism.merge_images(temp, y, x)
                imagehigh = imagehigh[0:w*4, 0:h*4]
                self.progressUpdated.emit(100)
                return imagehigh
            else:
                img = self.convertImage(im)
                highres = self.generator.predict(img)
                highres = cv2.convertScaleAbs(highres, alpha=(255.0))
                cv2.imwrite(temp + '/test.jpg', highres[0, :, :, ::-1])
                test = cv2.imread(temp + '/test.jpg')
                self.progressUpdated.emit(100)
                return test

    def convertImage(self, path):
        lr_img = cv2.imread(path)
        lr_img = cv2.cvtColor(lr_img, cv2.COLOR_BGR2RGB)
        lr_img = lr_img / 255
        lr_img = np.expand_dims(lr_img, axis=0)
        return lr_img
