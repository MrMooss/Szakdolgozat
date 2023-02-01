import cv2


def nearest_interpolation(path):
    img = cv2.imread(path)
    fx = 2
    fy = 2

    resized1 = cv2.resize(img, dsize=None, fx=fx, fy=fy, interpolation=cv2.INTER_NEAREST)

    cv2.imwrite("nearest.jpg", resized1)
    return resized1