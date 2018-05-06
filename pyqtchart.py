import sys
import random
import time

from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, QPointF
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtChart import QChart, QChartView, QLineSeries

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    chart = Chart()
    chart_view = QChartView(chart)
    chart_view.setRenderHint(QPainter.Antialiasing)
    chart.setTheme(QChart.ChartThemeDark)
    t = Thread()
    t.sig_append_pt.connect(chart.append_point)
    window.setCentralWidget(chart_view)
    window.resize(400, 300)
    window.show()
    t.start()
    sys.exit(app.exec_())

class Chart(QChart):

    def __init__(self):
        super().__init__()
        self.legend().hide()
        self.m_series = QLineSeries()
        self.addSeries(self.m_series)
        self.createDefaultAxes()

        self.x_max, self.x_min = 0, 0
        self.y_max, self.y_min = 0, 0

    @pyqtSlot(float, float)
    def append_point(self, x, y):
        self.m_series.append(x, y)
        self.x_max, self.x_min = max(x, self.x_max), min(x, self.x_min)
        self.y_max, self.y_min = max(y, self.y_max), min(y, self.y_min)
        if self.x_max - self.x_min > 100:
            self.axisX().setRange(self.x_max - 100, self.x_max)
        else:
            self.axisX().setRange(self.x_min, self.x_max)
        self.axisY().setRange(self.y_min - 5, self.y_max + 5)

class Thread(QThread):

    sig_append_pt = pyqtSignal(float, float)

    def __init__(self):
        super().__init__()

    def run(self):
        for x in range(0, 10000):
            self.sig_append_pt.emit(x, random.uniform(-10, 10))
            time.sleep(0.05)

if __name__ == '__main__':
    main()
