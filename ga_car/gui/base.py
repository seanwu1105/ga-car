""" Author: Sean Wu 104502551 NCU CSIE 3B

Define the GUI: main window.
"""

from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout

from .training_panel import TrainingPanel
from .testing_panel import TestingPanel

class GUIBase(QMainWindow):
    """ The base of GUI, containing the status bar and menu. """

    def __init__(self, maps, datasets):
        super().__init__()
        self.setWindowTitle("IT'S SO GENETIC")
        self.statusBar()
        self.setCentralWidget(BaseWidget(maps, datasets))

class BaseWidget(QWidget):

    def __init__(self, maps, datasets):
        super().__init__()
        layout = QHBoxLayout()
        panel_test = TestingPanel(maps)
        panel_train = TrainingPanel(datasets, panel_test)
        layout.addWidget(panel_train)
        layout.addWidget(panel_test)

        self.setLayout(layout)
