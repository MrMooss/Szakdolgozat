import unittest
from PIL import Image
import os
import numpy as np
import ImageSplitAndMerge as ism  # replace with the name of your module


class ImageProcessingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a test image
        cls.test_img = Image.new('RGB', (63, 63), color='red')
        cls.expanded_img = None

        # Save the image to a temporary file
        cls.test_img_path = 'temp_test_image.jpg'
        cls.test_img.save(cls.test_img_path)

    @classmethod
    def tearDownClass(cls):
        # Clean up: remove the temporary image file
        os.remove(cls.test_img_path)

    def test_expand_image(self):
        self.expanded_img = ism.expand_image(self.test_img)
        self.assertTrue(self.expanded_img.size[0] % 32 == 0 and self.expanded_img.size[1] % 32 == 0)

    def test_crop(self):
        temp_dir = 'temp_crop'
        os.makedirs(temp_dir, exist_ok=True)
        self.expanded_img = ism.expand_image(self.test_img)
        x, y = ism.crop(temp_dir, self.test_img)

        # Check if cropped images are created
        self.assertEqual((x, y), (2, 2))

        # Check dimensions of cropped images
        for f in os.listdir(temp_dir):
            img_path = os.path.join(temp_dir, f)
            with Image.open(img_path) as img:
                self.assertEqual(img.size, (32, 32))

        # Clean up
        for f in os.listdir(temp_dir):
            try:
                os.remove(os.path.join(temp_dir, f))
            except PermissionError as e:
                print(f"Error removing file {f}: {e}")

        os.rmdir(temp_dir)

    def test_merge_images(self):
        temp_dir = 'temp_crop'
        os.makedirs(temp_dir, exist_ok=True)
        self.expanded_img = ism.expand_image(self.test_img)
        w, h = ism.crop(temp_dir, self.expanded_img)

        # Merge images and test
        merged_array = ism.merge_images(temp_dir, h, w)

        expected_height, expected_width = h * 128, w * 128

        # Check if the merged array is correctly sized
        self.assertEqual((expected_height, expected_width), merged_array.shape[:2])

        # Clean up
        for f in os.listdir(temp_dir):
            try:
                os.remove(os.path.join(temp_dir, f))
            except PermissionError as e:
                print(f"Error removing file {f}: {e}")

        os.rmdir(temp_dir)

    def test_sliding_window(self):
        temp_dir = 'temp_patches'
        os.makedirs(temp_dir, exist_ok=True)
        self.expanded_img = ism.expand_image(self.test_img)
        patches, x_patches, y_patches = ism.sliding_window(temp_dir, self.expanded_img, 32)

        # Check if patches are created
        self.assertGreaterEqual(len(patches), 1)

        # Check if dimensions of patches are as expected
        for patch_path in patches:
            with Image.open(patch_path) as patch:
                self.assertEqual(patch.size, (32, 32))

        # Clean up
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))
        os.rmdir(temp_dir)

    def test_merge_patches(self):
        temp_dir = 'temp_patches'
        os.makedirs(temp_dir, exist_ok=True)
        self.expanded_img = ism.expand_image(self.test_img)
        patches, x_patches, y_patches = ism.sliding_window(temp_dir, self.expanded_img, 32)

        bgimg = np.zeros((63, 63, 3), dtype=np.uint8)
        merged_image = ism.merge_patches(temp_dir, 1, y_patches, x_patches, bgimg)

        # Check if the merged image is correctly sized
        self.assertEqual(merged_image.shape, (256, 256, 3))

        # Clean up
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))
        os.rmdir(temp_dir)


if __name__ == '__main__':
    unittest.main()