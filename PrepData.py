import cv2
import os
from tqdm import tqdm

train_dir = "Data"
for img in tqdm(os.listdir(train_dir + "/Data")):
    img_array = cv2.imread(train_dir + "/Data/" + img)

    img_array = cv2.resize(img_array, (128, 128))
    lr_img_array = cv2.resize(img_array, (32, 32))
    cv2.imwrite(train_dir + "/hr_images/" + img, img_array)
    cv2.imwrite(train_dir + "/lr_images/" + img, lr_img_array)