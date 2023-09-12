import cv2

def lanczos_interpolation(path):
    img = cv2.imread(path)
    fx = 4
    fy = 4
    resizedLanczos = cv2.resize(img, dsize=None, fx=fx, fy=fy, interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite("lanczos.jpg", resizedLanczos)
    return resizedLanczos