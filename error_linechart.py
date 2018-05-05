from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QVBoxLayout, QFrame
from PyQt5.QtChart import QChart, QChartView, QLineSeries

class ErrorLineChart(QFrame):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setMinimumHeight(200)
        self.setMinimumWidth(400)

        self.x_pts, self.y_pts = list(), list()
        self.series = QLineSeries()
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.legend().hide()
        self.chart.createDefaultAxes()
        self.chart.layout().setContentsMargins(0, 0, 0, 0)
        self.chart.setTheme(QChart.ChartThemeDark)
        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(chart_view)

    @pyqtSlot(float, float)
    def append_pt(self, x, y):
        self.x_pts.append(x)
        self.y_pts.append(y)
        self.series.append(x, y)
        x_max, x_min = max(self.x_list), min(self.x_list)
        if x_max - x_min > 500:
            self.chart.axisX().setRange(x_max - 500, x_max)
        else:
            self.chart.axisX().setRange(x_min, x_max)
        self.chart.axisY().setRange(min(self.y_list) - 5, max(self.y_list) + 5)
