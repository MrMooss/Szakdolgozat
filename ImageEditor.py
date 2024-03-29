from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QSlider, QPushButton, QHBoxLayout, QLabel, QGraphicsView,
    QGraphicsScene, QGraphicsPixmapItem
)
from PyQt5.QtGui import QImage, QPixmap, QPainter
import numpy as np
import cv2


class ImageAdjustmentDialog(QDialog):
    def __init__(self, image, interpol, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Adjustment")

        self.original_image = image
        self.adjusted_image = image.copy()
        self.interpol = interpol
        self.contrast = 100
        self.saturation = 100
        self.brightness = 0

        # Create QGraphicsView and QGraphicsScene
        self.graphics_view = QGraphicsView(self)
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setRenderHint(QPainter.Antialiasing, True)
        self.graphics_view.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.graphics_view.setFixedSize(400, 300)

        # Add QGraphicsPixmapItem to the QGraphicsScene
        self.pixmap_item = QGraphicsPixmapItem()
        self.graphics_scene.addItem(self.pixmap_item)
        self.pixmap_item.setPixmap(self.convert_cvimage_to_qpixmap(self.adjusted_image))

        # Create sliders for contrast, saturation, and brightness adjustments
        self.contrast_label = QLabel("Contrast", self)
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(1, 200)
        self.contrast_slider.setValue(self.contrast)

        self.saturation_label = QLabel("Saturation", self)
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setRange(0, 200)
        self.saturation_slider.setValue(self.saturation)

        self.brightness_label = QLabel("Brightness", self)
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(self.brightness)

        self.ok_button = QPushButton("Ok")
        self.cancel_button = QPushButton("Cancel")

        self.ok_button.clicked.connect(self.apply_adjustments)
        self.cancel_button.clicked.connect(self.cancel_adjustments)

        # Connect sliders to update the image preview
        self.contrast_slider.valueChanged.connect(self.update_preview)
        self.saturation_slider.valueChanged.connect(self.update_preview)
        self.brightness_slider.valueChanged.connect(self.update_preview)
        self.graphics_view.wheelEvent = self.zoom

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.graphics_view)
        layout.addWidget(self.contrast_label)
        layout.addWidget(self.contrast_slider)
        layout.addWidget(self.saturation_label)
        layout.addWidget(self.saturation_slider)
        layout.addWidget(self.brightness_label)
        layout.addWidget(self.brightness_slider)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def update_preview(self):

        contrast = self.contrast_slider.value()
        saturation = self.saturation_slider.value()
        brightness = self.brightness_slider.value()
        contrast /= 100.0
        saturation /= 100.0

        imghsv = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2HSV).astype("float32")
        (h, s, v) = cv2.split(imghsv)
        s *= saturation
        s = np.clip(s, 0, 255)
        imghsv = cv2.merge([h, s, v])
        rgb_image = cv2.cvtColor(imghsv.astype("uint8"), cv2.COLOR_HSV2RGB)
        cv2.convertScaleAbs(rgb_image, rgb_image, contrast, brightness)

        self.adjusted_image = rgb_image.copy()
        self.pixmap_item.setPixmap(self.convert_cvimage_to_qpixmap(self.adjusted_image))

    def convert_cvimage_to_qpixmap(self, image):
        height, width, channel = image.shape
        bytesPerLine = 3 * width
        qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        return QPixmap.fromImage(qImg)

    def apply_adjustments(self):
        self.accept()

    def cancel_adjustments(self):
        self.reject()

    def zoom(self, event):
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        self.graphics_view.scale(factor, factor)
