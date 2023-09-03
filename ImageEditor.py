from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QSlider, QPushButton, QHBoxLayout


class ImageAdjustmentDialog(QDialog):
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Adjustment")

        self.image = image
        self.adjusted_image = image.copy()  # Make a copy for adjustments

        # Create sliders for contrast, saturation, and brightness adjustments
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_slider.setValue(0)

        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setRange(-100, 100)
        self.saturation_slider.setValue(0)

        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)

        # Create Ok and Cancel buttons
        self.ok_button = QPushButton("Ok")
        self.cancel_button = QPushButton("Cancel")

        # Connect buttons to slots
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

        # TODO: Apply adjustments

        self.image = self.adjusted_image.copy()
        self.accept()

    def cancel_adjustments(self):
        # Close the dialog and discard the adjusted image
        self.reject()