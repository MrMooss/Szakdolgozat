from PyQt5.QtCore import QObject, pyqtSignal, QThread
from SuperResolution import SuperResolutionGenerator

class SuperResolutionWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        sr_generator = SuperResolutionGenerator()
        sr_generator.progressUpdated.connect(self.reportProgress)
        self.result_image = sr_generator.generateHr(self.path)
        self.finished.emit()

    def reportProgress(self, value):
        self.progress.emit(value)
