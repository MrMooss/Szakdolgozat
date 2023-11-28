from PIL import Image
import glob
import numpy as np
import cv2
import sys
import os

from LanczosInterpolation import lanczos_interpolation


# img = Image.open('test.jpg')
# h, w = img.size
# a, b = h, w
# while a % 32 != 0:
#     a = a + 1
# while b % 32 != 0:
#     b = b + 1
# img2 = img.crop((0, 0, a, b))
# img2.save('test_extended.jpg')
# w, h = img2.size
# x, y = 0, 0
# for i in range(0, h, 32):
#     y = 0
#     for j in range(0, w, 32):
#         c = img2.crop((j, i, j + 32, i + 32))
#         c.save('temp/' + str(x) + '-' + str(y) + '.jpg')
#         y += 1
#     x += 1
#
# images = [Image.open(x) for x in glob.glob('temp/*.jpg')]
# new_im = Image.new('RGB', (w, h))
#
# x_offset = 0
# y_offset = 0
# for im in images:
#     print(im.filename)
#     new_im.paste(im, (x_offset, y_offset))
#     x_offset += 32
#     print(x_offset, y_offset)
#     if x_offset == w:
#         x_offset = 0
#         y_offset += 32
# new_im.save('test_merged.jpg')


# expands the image, so it can be split into 32x32 subimages
def expand_image(img):
    h, w = img.size
    a, b = h, w
    while a % 32 != 0:
        a = a + 1
    while b % 32 != 0:
        b = b + 1
    img2 = img.crop((0, 0, a, b))

    return img2


def crop(path, img):
    w, h = img.size
    x, y = 0, 0
    n = 111111111111111
    for i in range(0, h, 32):
        y = 0
        for j in range(0, w, 32):
            c = img.crop((j, i, j + 32, i + 32))
            if c.mode == 'RGBA':
                c = c.convert('RGB')
            c.save(path + '/bg_' + str(n) + '.jpg')
            n += 1
            y += 1
        x += 1
    return x, y


# crops image to 32x32 subimages and saves them to the temp folder
def crop_and_pad(path, img):
    w, h = img.size
    x, y = 0, 0
    n = 111111111111111
    for i in range(0, h, 30):
        y = 0
        for j in range(0, w, 30):
            c = img.crop((j, i, j + 30, i + 30))

            # Add padding to make it 32x32
            pad = Image.new('RGB', (32, 32), (255, 255, 255))
            pad.paste(c, (1, 1))  # Add 1-pixel padding on all sides

            pad.save(path + '/' + str(n) + '.jpg')
            n += 1
            y += 1
        x += 1
    return x, y


# merges 128x128 images from a folder into one
def merge_images(path, w, h):
    imagelist = sorted(glob.glob(path + '/bg_*.jpg'))
    images = [Image.open(x) for x in imagelist]
    new_im = Image.new('RGB', (w*128, h*128))

    x_offset = 0
    y_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, y_offset))
        x_offset += 128
        if x_offset == w * 128:
            x_offset = 0
            y_offset += 128

    new_im_np = np.array(new_im)

    kernel_size = (5, 5)
    sigma = 0
    #smoothed_image = cv2.GaussianBlur(new_im_np, kernel_size, sigma)
    noise_removed = cv2.medianBlur(new_im_np, 3)
    return noise_removed


# Sliding window methods
def sliding_window(temp_dir, img, stride):
    patches = []
    h, w = img.size
    xdb, ydb = 0, 0
    for y in range(0, h, stride):
        for x in range(0, w, stride):
            patch = img.crop((x, y, x + 32, y + 32))
            if patch.mode == 'RGBA':
                patch = patch.convert('RGB')
            patch.save(os.path.join(temp_dir, f'patch_{x}_{y}.jpg'))
            patches.append(os.path.join(temp_dir, f'patch_{x}_{y}.jpg'))
        xdb += 1
    ydb = len(range(0, h, stride))
    return patches, xdb, ydb


def merge_patches(temp_dir, scale_factor, w, h, bgimg):
    patches = glob.glob(os.path.join(temp_dir, 'patch_*.jpg'))
    output = np.zeros((h * 128, w * 128, 3), dtype=np.uint8)
    output[0:bgimg.shape[0], 0:bgimg.shape[1]] = bgimg
    output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
    blend_strength = 0.5 # Adjust as needed

    for patch_path in patches:
        filename = os.path.splitext(os.path.basename(patch_path))[0]
        x_y = filename.split('_')[1:3]
        if len(x_y) == 2:
            x, y = map(int, x_y)
            hr_patch = cv2.imread(patch_path)

            start_x = x * scale_factor
            start_y = y * scale_factor
            end_x = start_x + hr_patch.shape[1] # Width of the patch
            end_y = start_y + hr_patch.shape[0] # Height of the patch

            # Blend the patched region into the output
            output[start_y:end_y, start_x:end_x] = cv2.addWeighted(
                output[start_y:end_y, start_x:end_x], blend_strength,
                hr_patch, 1 - blend_strength, 0
            )

        else:
            print(f"Skipping invalid filename: {filename}")

    output = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
    noise_removed = cv2.medianBlur(output, 3)
    return noise_removed
