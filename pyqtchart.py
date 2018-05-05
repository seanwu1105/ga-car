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
        self.x_list = list()
        self.y_list = list()
        self.m_series = QLineSeries()
        self.addSeries(self.m_series)
        self.createDefaultAxes()

    @pyqtSlot(float, float)
    def append_point(self, x, y):
        self.x_list.append(x)
        self.y_list.append(y)
        self.m_series.append(x, y)
        x_max, x_min = max(self.x_list), min(self.x_list)
        if x_max - x_min > 500:
            self.axisX().setRange(x_max - 500, x_max)
        else:
            self.axisX().setRange(x_min, x_max)
        self.axisY().setRange(min(self.y_list) - 5, max(self.y_list) + 5)

class Thread(QThread):

    sig_append_pt = pyqtSignal(float, float)

    def __init__(self):
        super().__init__()

    def run(self):
        for x in range(0, 10000):
            self.sig_append_pt.emit(x, random.uniform(0, 5))
            time.sleep(0.05)

if __name__ == '__main__':
    main()
