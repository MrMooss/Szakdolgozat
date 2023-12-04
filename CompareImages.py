import matplotlib.pyplot as plt
from matplotlib.image import imread
from tkinter import Tk
from tkinter import filedialog

def browse_image():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select Image")
    return file_path

def show_images():
    image1_path = browse_image()
    if not image1_path:
        print("No image selected. Exiting.")
        exit()

    image2_path = browse_image()
    if not image2_path:
        print("No second image selected. Exiting.")
        exit()

    image1 = imread(image1_path)
    image2 = imread(image2_path)

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    axes[0].imshow(image1)
    axes[0].set_title(image1_path[image1_path.rfind("/") + 1:])

    axes[1].imshow(image2)
    axes[1].set_title(image2_path[image2_path.rfind("/") + 1:])
    plt.show()
