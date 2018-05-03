""" The super class of all panels. """

from PyQt5.QtWidgets import QVBoxLayout, QFrame

class Panel(QFrame):
    def __init__(self):
        super().__init__()
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self._layout.setContentsMargins(0, 0, 0, 0)
