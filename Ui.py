import tempfile

from PyQt5.QtCore import Qt, QFileInfo
from PyQt5 import QtGui
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog, QPushButton, QDialog, QProgressDialog
import SuperResolution as sr
import cv2
import BicubicInterpolation as bi
import LinearInterpolation as li
import NearestNeighbourInterpolation as ni
import LanczosInterpolation as lancz
import shutil
import os

from ImageEditor import ImageAdjustmentDialog


class QImageViewer(QMainWindow):

    def __init__(self):
        super().__init__()

        self.interpol = False
        self.path = ''
        self.image = None
        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Light)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        
        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.scrollArea.setVisible(False)

        self.setCentralWidget(self.scrollArea)

        self.createActions()
        self.createMenus()

        self.setWindowTitle("Super-resolution")
        self.resize(800, 600)

    def open(self):
        options = QFileDialog.Options()
        # fileName = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath())
        fileName, _ = QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileName()', '',
                                                'Images (*.png *.jpeg *.jpg *.bmp *.gif)', options=options)
        if fileName:
            self.path = fileName
            self.image = cv2.imread(fileName)
            image = QImage(fileName)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer", "Cannot load %s." % fileName)
                return
            self.imageLabel.setPixmap(QPixmap.fromImage(image))
            self.scaleFactor = 1.0
            self.srAct.setEnabled(True)
            self.bicubicAct.setEnabled(True)
            self.linearAct.setEnabled(True)
            self.lanczosAct.setEnabled(True)
            self.nearestAct.setEnabled(True)
            self.adjustImageAct.setEnabled(True)
            self.scrollArea.setVisible(True)
            self.fitToWindowAct.setEnabled(True)
            self.saveImageAct.setEnabled(True)
            self.updateActions()
            self.adjust_dialog = ImageAdjustmentDialog(self.image, self.interpol)
            
            if not self.fitToWindowAct.isChecked():
                self.imageLabel.adjustSize()

    def adjust_image(self):
        if self.image is not None:
            # Create an instance of the ImageAdjustmentDialog class
            # adjust_dialog = ImageAdjustmentDialog(self.image, self.interpol)
            result = self.adjust_dialog.exec_()
            if result == QDialog.Accepted:
                self.interpol = self.adjust_dialog.interpol
                height, width, channel = self.adjust_dialog.adjusted_image.shape
                bytesPerLine = 3 * width
                qImg = QImage(self.adjust_dialog.adjusted_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
                img = QImage(qImg)
                self.image = self.adjust_dialog.adjusted_image
                self.imageLabel.setPixmap(QPixmap.fromImage(img))
                self.normalSize()

                if not self.fitToWindowAct.isChecked():
                    self.imageLabel.adjustSize()

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()

        self.updateActions()

    def superRes(self):
        if self.path != '':
            self.adjust_dialog.interpol = False
            loading_dialog = QProgressDialog("Super-Res in progress...", None, 0, 0, self)
            loading_dialog.setWindowModality(Qt.WindowModal)
            loading_dialog.setWindowTitle("Loading")
            loading_dialog.setCancelButton(None)
            loading_dialog.show()
            qApp.processEvents()

            img = sr.generateHr(self.path)
            loading_dialog.close()
            self.image = img
            img_bytes = img.tobytes()

            width = img.shape[1]
            height = img.shape[0]
            bytes_per_line = img.shape[1] * 3

            # Create a QImage from the bytes
            img = QImage(img_bytes, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)

            self.imageLabel.setPixmap(QPixmap.fromImage(img))
            self.normalSize()

            if not self.fitToWindowAct.isChecked():
                self.imageLabel.adjustSize()

    def bicubic(self):
        if self.path != '':
            self.adjust_dialog.interpol = True
            img = bi.bicubic_interpolation(self.path)
            self.image = img
            # p = QImage(img, img.shape[1], img.shape[0], img.strides[0], QtGui.QImage.Format_RGB888)
            # self.imageLabel.setPixmap(QPixmap.fromImage(p))
            self.imageLabel.setPixmap(QPixmap('bicubic.jpg'))
            os.remove('bicubic.jpg')
            self.normalSize()

    def linear(self):
        if self.path != '':
            self.adjust_dialog.interpol = True
            img = li.linear_interpolation(self.path)
            self.image = img
            # p = QImage(img, img.shape[1], img.shape[0], img.strides[0], QtGui.QImage.Format_RGB888)
            # self.imageLabel.setPixmap(QPixmap.fromImage(p))
            self.imageLabel.setPixmap(QPixmap('linearx2.jpg'))
            os.remove('linearx2.jpg')
            self.normalSize()

    def lanczos(self):
        if self.path != '':
            self.adjust_dialog.interpol = True
            img = lancz.lanczos_interpolation(self.path)
            self.image = img
            # p = QImage(img, img.shape[1], img.shape[0], img.strides[0], QtGui.QImage.Format_RGB888)
            # self.imageLabel.setPixmap(QPixmap.fromImage(p))
            self.imageLabel.setPixmap(QPixmap('lanczos.jpg'))
            os.remove('lanczos.jpg')
            self.normalSize()

    def nearest(self):
        if self.path != '':
            self.adjust_dialog.interpol = True
            img = ni.nearest_interpolation(self.path)
            self.image = img
            # p = QImage(img, img.shape[1], img.shape[0], img.strides[0], QtGui.QImage.Format_RGB888)
            # self.imageLabel.setPixmap(QPixmap.fromImage(p))
            self.imageLabel.setPixmap(QPixmap('nearest.jpg'))
            os.remove('nearest.jpg')
            self.normalSize()

    def savePic(self):
        if self.image is not None:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            filename, _ = QFileDialog.getSaveFileName(self, filter="JPG(*.jpg);;PNG(*.png);;TIFF(*.tiff);;BMP(*.bmp)")
            if filename:
                rgb_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                cv2.imwrite(filename, rgb_image)


    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
        self.srAct = QAction("&Enhance", self, enabled=False, triggered=self.superRes)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)
        self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False, checkable=True, shortcut="Ctrl+F",
                                      triggered=self.fitToWindow)
        self.saveImageAct = QAction("&Save", self, enabled=False, triggered=self.savePic)
        self.bicubicAct = QAction("&Bicub", self, enabled=False, triggered=self.bicubic)
        self.linearAct = QAction("&Linear", self, enabled=False, triggered=self.linear)
        self.nearestAct = QAction("&Nearest", self, enabled=False, triggered=self.nearest)
        self.lanczosAct = QAction("&Lanczos", self, enabled=False, triggered=self.lanczos)
        self.adjustImageAct = QAction("Adjust Image", self, enabled=False, triggered=self.adjust_image)



    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)
        self.fileMenu.addAction(self.saveImageAct)

        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.picsMenu = QMenu("&Edit", self)
        self.picsMenu.addAction(self.srAct)
        self.picsMenu.addAction(self.bicubicAct)
        self.picsMenu.addAction(self.linearAct)
        self.picsMenu.addAction(self.nearestAct)
        self.picsMenu.addAction(self.lanczosAct)
        self.picsMenu.addAction(self.adjustImageAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.picsMenu)

    def updateActions(self):
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                               + ((factor - 1) * scrollBar.pageStep() / 2)))


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    imageViewer = QImageViewer()
    imageViewer.show()
    sys.exit(app.exec_())