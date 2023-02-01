from PIL import Image
import glob
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


# expands the image so it can be split into 32x32 subimages
def expand_image(img):
    h, w = img.size
    a, b = h, w
    while a % 32 != 0:
        a = a + 1
    while b % 32 != 0:
        b = b + 1
    img2 = img.crop((0, 0, a, b))

    return img2


# crops image to 32x32 subimages and saves them to the temp folder
def crop(path, img):
    w, h = img.size
    x, y = 0, 0
    n = 111111111111111
    for i in range(0, h, 32):
        y = 0
        for j in range(0, w, 32):
            c = img.crop((j, i, j + 32, i + 32))
            c.save(path + '/' + str(n) + '.jpg')
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
    return new_im