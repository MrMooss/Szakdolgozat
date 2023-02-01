import GAN as gan
import os
import cv2
import numpy as np
import random
import matplotlib.pyplot as plt
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from keras.layers import *
from keras.models import load_model

lr_path = 'Data/lr_images'
hr_path = 'Data/hr_images'
lr_list = os.listdir(lr_path)
lr_list.sort()
lr_images = []
for img in tqdm(lr_list):
    lr_img = cv2.imread(lr_path + "/" + img)
    lr_img = cv2.cvtColor(lr_img, cv2.COLOR_BGR2RGB)
    lr_images.append(lr_img)

hr_list = os.listdir(hr_path)
hr_list.sort()
hr_images = []
for img in tqdm(hr_list):
    hr_img = cv2.imread(hr_path + "/" + img)
    hr_img = cv2.cvtColor(hr_img, cv2.COLOR_BGR2RGB)
    hr_images.append(hr_img)

hr_images_full = np.array(hr_images)
lr_images_full = np.array(lr_images)

for i in tqdm(range(4)):
  limit = 5000*(i+1)
  hr_images = hr_images_full[limit-5000:limit] / 255
  lr_images = lr_images_full[limit-5000:limit] / 255

lr_train, lr_test, hr_train, hr_test = train_test_split(lr_images, hr_images, test_size=0.30, random_state=42)

hr_shape = (hr_train.shape[1], hr_train.shape[2], hr_train.shape[3])
lr_shape = (lr_train.shape[1], lr_train.shape[2], lr_train.shape[3])
hr_in = Input(shape=hr_shape)
lr_in = Input(shape=lr_shape)

gen = load_model('gen_e_25.h5', compile=False)
dis = gan.discriminator(hr_in)
dis.compile(loss="binary_crossentropy", optimizer="adam", metrics=['accuracy'])

vgg = gan.build_vgg((128,128,3))
vgg.trainable = False

gan_model1 = gan.createGan(gen, dis, vgg, lr_in, hr_in)

gan_model1.compile(loss=["binary_crossentropy", "mse"], loss_weights=[1e-3, 1], optimizer="adam")

batch_size = 1
train_lr_batches = []
train_hr_batches = []
for i in range(int(hr_train.shape[0] / batch_size)):
    start = i * batch_size
    end = start + batch_size
    train_hr_batches.append(hr_train[start:end])
    train_lr_batches.append(lr_train[start:end])


epochs = 30
for e in range(epochs):
    fake_label = np.zeros((batch_size, 1))
    real_label = np.ones((batch_size, 1))
    g_losses = []
    d_losses = []

    for b in tqdm(range(len(train_hr_batches))):
      lr_imgs = train_lr_batches[b]
      hr_imgs = train_hr_batches[b]

      fake_imgs = gen.predict_on_batch(lr_imgs)

      dis.trainable = True
      d_loss_gen = dis.train_on_batch(fake_imgs, fake_label)
      d_loss_real = dis.train_on_batch(hr_imgs, real_label)

      dis.trainable = False

      d_loss = 0.5 * np.add(d_loss_gen, d_loss_real)

      image_features = vgg.predict(hr_imgs)

      g_loss, = gan_model1.train_on_batch([lr_imgs, hr_imgs], [real_label, image_features])

      d_losses.append(d_loss)
      g_losses.append(g_loss)

    g_losses = np.array(g_losses)
    d_losses = np.array(d_losses)

    print("epoch:", e + 1, "g_loss:", g_loss, "d_loss:", d_loss)
    if (e + 1) % 5 == 0:
      gen.save("gene" + str(e + 1) + ".h5")
      dis.save("dise" + str(e + 1) + ".h5")