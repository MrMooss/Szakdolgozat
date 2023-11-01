from PIL import Image
import glob
import numpy as np
import cv2
import sys
import os

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
                # Convert RGBA to RGB
                c = c.convert('RGB')
            c.save(path + '/' + str(n) + '.jpg')
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
    imagelist = sorted(glob.glob(path + '/*.jpg'))
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


def merge_pad_images(path, w, h):
    imagelist = sorted(glob.glob(path + '/*.jpg'))
    images = [Image.open(x) for x in imagelist]
    new_im = Image.new('RGB', (w*120, h*120))

    x_offset = 0
    y_offset = 0
    for im in images:
        # Remove the 1-pixel padding
        im = im.crop((4, 4, 124, 124))
        new_im.paste(im, (x_offset, y_offset))
        x_offset += 120
        if x_offset == w * 120:
            x_offset = 0
            y_offset += 120
    return new_im

def blend_merge(path):
    imagelist = sorted(glob.glob(path + '/*.jpg'))
    images = [cv2.imread(x) for x in imagelist]
    # Determine the overlap size (e.g., 10 pixels)
    overlap_size = 1

    # Calculate the final size of the merged image
    merged_height = len(images) * images[0].shape[0] - (len(images) - 1) * overlap_size
    merged_width = images[0].shape[1]

    # Create an empty canvas for the merged image
    merged_image = np.zeros((merged_height, merged_width, 3), dtype=np.uint8)

    # Initialize starting y-coordinate for pasting images
    y_start = 0

    # Iterate through the images and paste them with overlap
    for image in images:
        merged_image[y_start:y_start + image.shape[0], :] = image
        y_start += image.shape[0] - overlap_size
    return merged_image