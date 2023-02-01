from PyQt5.QtCore import Qt, QFileInfo
from PyQt5 import QtGui
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog
import SuperResolution as sr
import cv2
import BicubicInterpolation as bi
import LinearInterpolation as li
import NearestNeighbourInterpolation as ni


class QImageViewer(QMainWindow):

    def __init__(self):
        super().__init__()

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
            image = QImage(fileName)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer", "Cannot load %s." % fileName)
                return

            self.imageLabel.setPixmap(QPixmap.fromImage(image))
            self.scaleFactor = 1.0
            self.srAct.setEnabled(True)
            self.bicubicAct.setEnabled(True)
            self.linearAct.setEnabled(True)
            self.nearestAct.setEnabled(True)
            self.scrollArea.setVisible(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

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
            img = sr.generateHr(self.path)
            self.image = img
            img = QImage(img, img.shape[1], img.shape[0], img.strides[0], QtGui.QImage.Format_BGR888)
            self.imageLabel.setPixmap(QPixmap.fromImage(img))
            self.normalSize()

            if not self.fitToWindowAct.isChecked():
                self.imageLabel.adjustSize()

    def bicubic(self):
        if self.path != '':
            img = bi.bicubic_interpolation(self.path)
            self.image = img
            # p = QImage(img, img.shape[1], img.shape[0], img.strides[0], QtGui.QImage.Format_RGB888)
            # self.imageLabel.setPixmap(QPixmap.fromImage(p))
            self.imageLabel.setPixmap(QPixmap('bicubic.jpg'))
            self.normalSize()

    def linear(self):
        if self.path != '':
            img = li.linear_interpolation(self.path)
            self.image = img
            # p = QImage(img, img.shape[1], img.shape[0], img.strides[0], QtGui.QImage.Format_RGB888)
            # self.imageLabel.setPixmap(QPixmap.fromImage(p))
            self.imageLabel.setPixmap(QPixmap('linear.jpg'))
            self.normalSize()

    def nearest(self):
        if self.path != '':
            img = ni.nearest_interpolation(self.path)
            self.image = img
            # p = QImage(img, img.shape[1], img.shape[0], img.strides[0], QtGui.QImage.Format_RGB888)
            # self.imageLabel.setPixmap(QPixmap.fromImage(p))
            self.imageLabel.setPixmap(QPixmap('nearest.jpg'))
            self.normalSize()

    def savePic(self):
        filename = QFileDialog.getSaveFileName(filter="JPG(.jpg);;PNG(.png);;TIFF(.tiff);;BMP(.bmp)")[0]
        cv2.imwrite(filename, self.image)

    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
        self.srAct = QAction("&Enhance", self, enabled=False, triggered=self.superRes)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)
        self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False, checkable=True, shortcut="Ctrl+F",
                                      triggered=self.fitToWindow)
        self.bicubicAct = QAction("&Bicub", self, enabled=False, triggered=self.bicubic)
        self.linearAct = QAction("&Linear", self, enabled=False, triggered=self.linear)
        self.nearestAct = QAction("&Nearest", self, enabled=False, triggered=self.nearest)



    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.picsMenu = QMenu("&Edit", self)
        self.picsMenu.addAction(self.srAct)
        self.picsMenu.addAction(self.bicubicAct)
        self.picsMenu.addAction(self.linearAct)
        self.picsMenu.addAction(self.nearestAct)


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