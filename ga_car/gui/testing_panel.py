""" Define the contents of testing panel. """

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import (QHBoxLayout, QFormLayout, QGroupBox, QComboBox,
                             QPushButton, QLabel, QTextEdit, QSpinBox)

from .panel import Panel
from .car_simulator_plot import CarSimulatorPlot
from ..backend.car import Car
from ..backend.run import RunCar
from ..backend.rbfn import RBFN


class TestingPanel(Panel):

    def __init__(self, maps):
        super().__init__()
        self.maps = maps
        self.rbfn = None

        self.__set_execution_ui()
        self.__set_outputs_ui()
        self.__set_graphic_ui()
        self.__set_console_ui()

    def __set_execution_ui(self):
        group_box = QGroupBox('Testing Execution')
        inner_layout = QHBoxLayout()
        group_box.setLayout(inner_layout)

        self.map_selector = QComboBox()
        self.map_selector.addItems(self.maps.keys())
        self.map_selector.setStatusTip('Select the training dataset.')
        self.map_selector.currentIndexChanged.connect(self.__change_map)

        self.start_btn = QPushButton('Test')
        self.start_btn.setStatusTip('Start testing. (available after training)')
        self.start_btn.setDisabled(True)
        self.start_btn.clicked.connect(self.__run)

        self.stop_btn = QPushButton('Stop')
        self.stop_btn.setStatusTip('Force the testing stop running.')
        self.stop_btn.setDisabled(True)

        self.fps = QSpinBox()
        self.fps.setMinimum(1)
        self.fps.setMaximum(60)
        self.fps.setValue(20)
        self.fps.setStatusTip("The re-drawing rate for car simulator. High fps "
                              "may cause the plot shows discontinuously.")

        inner_layout.addWidget(self.map_selector, 1)
        inner_layout.addWidget(QLabel("FPS:"))
        inner_layout.addWidget(self.fps)
        inner_layout.addWidget(self.start_btn)
        inner_layout.addWidget(self.stop_btn)

        self._layout.addWidget(group_box)

    def __set_outputs_ui(self):
        group_box = QGroupBox("Testing Details")
        inner_layout = QFormLayout()
        group_box.setLayout(inner_layout)

        self.car_position = QLabel('--')
        self.car_angle = QLabel('--')
        self.wheel_angle = QLabel('--')
        self.dist_front = QLabel('--')
        self.dist_left = QLabel('--')
        self.dist_right = QLabel('--')

        self.car_position.setAlignment(Qt.AlignCenter)
        self.car_angle.setAlignment(Qt.AlignCenter)
        self.wheel_angle.setAlignment(Qt.AlignCenter)
        self.dist_front.setAlignment(Qt.AlignCenter)
        self.dist_left.setAlignment(Qt.AlignCenter)
        self.dist_right.setAlignment(Qt.AlignCenter)

        inner_layout.addRow('Car Position:', self.car_position)
        inner_layout.addRow('Car Angle:', self.car_angle)
        inner_layout.addRow('Wheel Angle:', self.wheel_angle)
        inner_layout.addRow('Front Distance:', self.dist_front)
        inner_layout.addRow('Left Distance:', self.dist_left)
        inner_layout.addRow('Right Distance:', self.dist_right)

        self._layout.addWidget(group_box)

    def __set_graphic_ui(self):
        self.simulator = CarSimulatorPlot()
        self.simulator.setStatusTip("Show the graphic of the car controled by "
                                    "the result of genetic algorithm in mazz.")
        self.__change_map()
        self._layout.addWidget(self.simulator)

    def __set_console_ui(self):
        self.__console = QTextEdit()
        self.__console.setReadOnly(True)
        self.__console.setStatusTip("Show the logs of status changing.")
        self._layout.addWidget(self.__console)

    @pyqtSlot()
    def __init_widgets(self):
        self.start_btn.setDisabled(True)
        self.stop_btn.setEnabled(True)
        self.fps.setDisabled(True)
        self.map_selector.setDisabled(True)

    @pyqtSlot()
    def __reset_widgets(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setDisabled(True)
        self.fps.setEnabled(True)
        self.map_selector.setEnabled(True)

    @pyqtSlot(str)
    def print_console(self, text):
        self.__console.append(text)

    @pyqtSlot(list, list, list)
    def __show_dists(self, pos, intersections, dists):
        self.simulator.paint_dist(pos, intersections)
        self.dist_front.setText(str(dists[0]))
        self.dist_left.setText(str(dists[1]))
        self.dist_right.setText(str(dists[2]))

    @pyqtSlot()
    def __show_car_collided(self):
        self.simulator.paint_car_collided()

    def __show_path(self, xdata, ydata):
        self.simulator.paint_path(xdata, ydata)

    @pyqtSlot()
    def __change_map(self):
        self.__current_map = self.maps[self.map_selector.currentText()]
        self.__car = Car(self.__current_map['start_pos'],
                         self.__current_map['start_angle'],
                         3, self.__current_map['route_edge'])
        self.simulator.paint_map(self.__current_map)
        self.__move_car(self.__current_map['start_pos'],
                        self.__current_map['start_angle'])
        self.__show_dists(self.__current_map['start_pos'],
                          [self.__current_map['start_pos']] * 3, ['--'] * 3)

    @pyqtSlot(list, float, float)
    def __move_car(self, pos, angle, wheel_angle=0.0):
        self.simulator.paint_car(pos, angle)
        self.car_position.setText("({:.7f}, {:.7f})".format(*pos))
        self.car_angle.setText(str(angle))
        self.wheel_angle.setText(str(wheel_angle))

    @pyqtSlot(RBFN)
    def load_rbfn(self, rbfn):
        self.rbfn = rbfn
        self.print_console('New RBFN model has been loaded.')
        self.start_btn.setEnabled(True)

    @pyqtSlot()
    def __run(self):
        # reset the map
        self.__change_map()
        # create a QThread
        if self.rbfn is None:
            raise TypeError('The RBFN model has not yet loaded.')
        self.__thread = RunCar(self.__car, self.rbfn,
                               (self.__current_map['end_area_lt'],
                                self.__current_map['end_area_rb']),
                               self.fps.value())
        self.stop_btn.clicked.connect(self.__thread.stop)
        self.__thread.started.connect(self.__init_widgets)
        self.__thread.finished.connect(self.__reset_widgets)
        self.__thread.sig_console.connect(self.print_console)
        self.__thread.sig_car.connect(self.__move_car)
        self.__thread.sig_car_collided.connect(self.__show_car_collided)
        self.__thread.sig_dists.connect(self.__show_dists)
        self.__thread.sig_results.connect(self.__get_results)
        self.__thread.start()

    @pyqtSlot(list)
    def __get_results(self, results):
        """Get the results of last running and draw the path of it."""
        self.simulator.paint_path([d['x'] for d in results], [d['y'] for d in results])
