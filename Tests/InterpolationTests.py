import unittest
import os
from PIL import Image
import numpy as np
from BicubicInterpolation import bicubic_interpolation
from LanczosInterpolation import lanczos_interpolation
from LinearInterpolation import linear_interpolation
from NearestNeighbourInterpolation import nearest_interpolation

class ImageProcessingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_img = Image.new('RGB', (40, 40), color='red')
        cls.test_img_path = 'temp_test_image.jpg'
        cls.test_img.save(cls.test_img_path)
        cls.ratio = 4

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.test_img_path)

    def test_bicubic_interpolation(self):
        result_image = bicubic_interpolation(self.test_img_path)
        self.assertIsInstance(result_image, np.ndarray, "Result should be a numpy array")
        expected_height = self.test_img.height * self.ratio
        expected_width = self.test_img.width * self.ratio
        self.assertEqual(result_image.shape[0], expected_height, "Height of the image does not match expected")
        self.assertEqual(result_image.shape[1], expected_width, "Width of the image does not match expected")
        os.remove("bicubic.jpg")

    def test_linear_interpolation(self):
        result_image = linear_interpolation(self.test_img_path)
        self.assertIsInstance(result_image, np.ndarray, "Result should be a numpy array")
        self.assertGreaterEqual(result_image.shape[0], self.test_img.height * 2)
        self.assertGreaterEqual(result_image.shape[1], self.test_img.width * 2)
        os.remove("linearx2.jpg")

    def test_lanczos_interpolation(self):
        result_image = lanczos_interpolation(self.test_img_path)
        self.assertIsInstance(result_image, np.ndarray, "Result should be a numpy array")
        self.assertEqual(result_image.shape[0], self.test_img.height * self.ratio)
        self.assertEqual(result_image.shape[1], self.test_img.width * self.ratio)
        os.remove("lanczos.jpg")

    def test_nearest_interpolation(self):
        result_image = nearest_interpolation(self.test_img_path)
        self.assertIsInstance(result_image, np.ndarray, "Result should be a numpy array")
        self.assertEqual(result_image.shape[0], self.test_img.height * self.ratio)
        self.assertEqual(result_image.shape[1], self.test_img.width * self.ratio)
        os.remove("nearest.jpg")


if __name__ == '__main__':
    unittest.main()