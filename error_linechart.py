from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QVBoxLayout, QFrame
from PyQt5.QtChart import QChart, QChartView, QLineSeries

class ErrorLineChart(QFrame):

    def __init__(self, nseries=1, series_names=None):
        super().__init__()
        if nseries < 1:
            raise ValueError('The number of serieses must be larger than zero.')
        self.nseries = nseries
        self.series_names = series_names
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setMinimumHeight(110)
        self.setMinimumWidth(400)

        self.serieses = [QLineSeries() for _ in range(self.nseries)]
        self.chart = QChart()
        if self.series_names is None:
            self.chart.legend().hide()
        for idx, series in enumerate(self.serieses):
            self.chart.addSeries(series)
            if self.series_names is not None:
                series.setName(self.series_names[idx])
        self.chart.createDefaultAxes()
        self.chart.layout().setContentsMargins(0, 0, 0, 0)
        # self.chart.setTheme(QChart.ChartThemeDark)
        self.chart.axisY().setTickCount(3)
        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(chart_view)

        self.x_max = 2
        self.y_pts = list()

    def append_point(self, x, y, series_idx=0):
        self.serieses[series_idx].append(x, y)
        self.x_max = max(x, self.x_max)
        self.y_pts.append(y)
        if self.x_max > 100:
            self.chart.axisX().setRange(self.x_max - 100, self.x_max)
            y_max = max(self.y_pts[-100:])
            self.serieses[series_idx].remove(self.x_max - 100, self.y_pts[self.x_max - 101])
        else:
            self.chart.axisX().setRange(1, self.x_max)
            y_max = max(self.y_pts)
        self.chart.axisY().setRange(0, y_max + y_max / 5)

    def clear(self):
        self.chart.removeAllSeries()
        self.serieses = [QLineSeries() for _ in range(self.nseries)]
        for idx, series in enumerate(self.serieses):
            self.chart.addSeries(series)
            if self.series_names is not None:
                series.setName(self.series_names[idx])
        self.chart.createDefaultAxes()
        self.chart.axisY().setTickCount(3)
        self.x_max = 2
        self.y_pts = list()
