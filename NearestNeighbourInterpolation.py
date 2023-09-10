import cv2


def nearest_interpolation(path):
    img = cv2.imread(path)
    fx = 4
    fy = 4

    resized = cv2.resize(img, dsize=None, fx=fx, fy=fy, interpolation=cv2.INTER_NEAREST)


    cv2.imwrite("nearest.jpg", resized)
    return resized