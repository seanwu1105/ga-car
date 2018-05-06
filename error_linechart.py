from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QVBoxLayout, QFrame
from PyQt5.QtChart import QChart, QChartView, QLineSeries

class ErrorLineChart(QFrame):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setMinimumHeight(150)
        self.setMinimumWidth(400)

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

        self.x_max = 2
        self.y_pts = list()

    def append_point(self, x, y):
        self.series.append(x, y)
        self.x_max = max(x, self.x_max)
        self.y_pts.append(y)
        if self.x_max > 100:
            self.chart.axisX().setRange(self.x_max - 100, self.x_max)
            y_max = max(self.y_pts[-100:])
            self.series.remove(self.x_max - 100, self.y_pts[self.x_max - 101])
        else:
            self.chart.axisX().setRange(1, self.x_max)
            y_max = max(self.y_pts)
        self.chart.axisY().setRange(0, y_max + y_max / 5)

    def clear(self):
        self.chart.removeAllSeries()
        self.series = QLineSeries()
        self.chart.addSeries(self.series)
        self.chart.createDefaultAxes()
        self.x_max = 2
        self.y_pts = list()
