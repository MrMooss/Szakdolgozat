from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QSlider, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtGui import QImage
from PIL import Image, ImageEnhance
import cv2


class ImageAdjustmentDialog(QDialog):
    def __init__(self, image, interpol, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Adjustment")

        self.image = image
        self.adjusted_image = image.copy()
        self.interpol = interpol
        self.contrast = 0
        self.saturation = 0
        self.brightness = 0

        # Create sliders for contrast, saturation, and brightness adjustments
        self.contrast_label = QLabel("Contrast", self)
        self.contrast_label.move(10,-5)
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(0, 200)
        self.contrast_slider.setValue(100)

        self.saturation_label = QLabel("Saturation", self)
        self.saturation_label.move(10, 23)
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setRange(000, 200)
        self.saturation_slider.setValue(100)

        self.brightness_label = QLabel("Brightness", self)
        self.brightness_label.move(10, 51)
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)

        self.ok_button = QPushButton("Ok")
        self.cancel_button = QPushButton("Cancel")

        self.ok_button.clicked.connect(self.apply_adjustments)
        self.cancel_button.clicked.connect(self.cancel_adjustments)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.contrast_slider)
        layout.addWidget(self.saturation_slider)
        layout.addWidget(self.brightness_slider)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def apply_adjustments(self):
        contrast = self.contrast_slider.value()
        saturation = self.saturation_slider.value()
        brightness = self.brightness_slider.value()
        contrast = contrast / 100
        saturation = saturation / 100

        #data = Image.fromarray(self.adjusted_image)
        #filter = ImageEnhance.Color(data)
        #self.adjusted_image = self.adjusted_image.filter(saturation)
        rgb_image = self.adjusted_image
        if self.interpol:
            rgb_image = cv2.cvtColor(self.adjusted_image, cv2.COLOR_BGR2RGB)
            self.interpol = False

        cv2.convertScaleAbs(rgb_image, rgb_image, contrast, brightness)

        self.image = rgb_image.copy()
        self.accept()

    def cancel_adjustments(self):
        self.reject()