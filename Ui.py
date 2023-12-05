import tempfile

from PyQt5.QtCore import Qt, QFileInfo, QObject, pyqtSignal, QThread
from PyQt5 import QtGui
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog, QPushButton, QDialog, QProgressDialog
from SuperResWorker import SuperResolutionWorker
import cv2
import BicubicInterpolation as bi
import LinearInterpolation as li
import NearestNeighbourInterpolation as ni
import LanczosInterpolation as lancz
import shutil
import os
from CompareImages import show_images

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
        self.adjust_dialog = None

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
            
            if not self.fitToWindowAct.isChecked():
                self.imageLabel.adjustSize()

    def adjust_image(self):
        if self.image is not None:
            if self.interpol:
                self.image = cv2.convertScaleAbs(self.image)
                self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.adjust_dialog = ImageAdjustmentDialog(self.image, self.interpol)
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
                self.interpol = False

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
            self.interpol = False
            self.loading_dialog = QProgressDialog("Super-Res in progress...", None, 0, 100, self)
            self.loading_dialog.setWindowModality(Qt.WindowModal)
            self.loading_dialog.setWindowTitle("Loading")
            self.loading_dialog.setCancelButton(None)
            self.loading_dialog.show()

            # Setup the thread and worker
            self.thread = QThread()
            self.worker = SuperResolutionWorker(self.path)
            self.worker.moveToThread(self.thread)

            # Connect signals and slots
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.progress.connect(self.updateProgress)
            self.worker.finished.connect(self.onSuperResFinished)

            # Start the thread
            self.thread.start()

    def updateProgress(self, value):
        self.loading_dialog.setValue(value)

    def onSuperResFinished(self):
        self.loading_dialog.close()
        self.image = self.worker.result_image
        img_bytes = self.image.tobytes()
        width = self.image.shape[1]
        height = self.image.shape[0]
        bytes_per_line = self.image.shape[1] * 3

        # Create a QImage from the bytes
        img = QImage(img_bytes, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
        self.imageLabel.setPixmap(QPixmap.fromImage(img))
        self.normalSize()
        if not self.fitToWindowAct.isChecked():
            self.imageLabel.adjustSize()
            
    def updateProgress(self, value):
        self.loading_dialog.setValue(value)
    
    def bicubic(self):
        if self.path != '':
            self.interpol = True
            img = bi.bicubic_interpolation(self.path)
            self.image = img
            # p = QImage(img, img.shape[1], img.shape[0], img.strides[0], QtGui.QImage.Format_RGB888)
            # self.imageLabel.setPixmap(QPixmap.fromImage(p))
            self.imageLabel.setPixmap(QPixmap('bicubic.jpg'))
            os.remove('bicubic.jpg')
            self.normalSize()

    def compare(self):
        show_images()

    def linear(self):
        if self.path != '':
            self.interpol = True
            img = li.linear_interpolation(self.path)
            self.image = img
            # p = QImage(img, img.shape[1], img.shape[0], img.strides[0], QtGui.QImage.Format_RGB888)
            # self.imageLabel.setPixmap(QPixmap.fromImage(p))
            self.imageLabel.setPixmap(QPixmap('linearx2.jpg'))
            os.remove('linearx2.jpg')
            self.normalSize()

    def lanczos(self):
        if self.path != '':
            self.interpol = True
            img = lancz.lanczos_interpolation(self.path)
            self.image = img
            # p = QImage(img, img.shape[1], img.shape[0], img.strides[0], QtGui.QImage.Format_RGB888)
            # self.imageLabel.setPixmap(QPixmap.fromImage(p))
            self.imageLabel.setPixmap(QPixmap('lanczos.jpg'))
            os.remove('lanczos.jpg')
            self.normalSize()

    def nearest(self):
        if self.path != '':
            self.interpol = True
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
                rgb_image = cv2.convertScaleAbs(self.image)
                if not self.interpol:
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
        self.compare = QAction("Compare Images", self, enabled=True, triggered=self.compare)



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
        self.viewMenu.addAction(self.compare)

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