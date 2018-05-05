""" Define the contents of training panel. """

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QHBoxLayout, QFormLayout, QGroupBox, QPushButton,
                             QComboBox, QSpinBox, QDoubleSpinBox, QLabel)

from panel import Panel
from testing_panel import TestingPanel
from error_linechart import ErrorLineChart


class TrainingPanel(Panel):

    def __init__(self, datasets, testing_panel):
        super().__init__()
        if isinstance(testing_panel, TestingPanel):
            self.graphic_panel = testing_panel
        else:
            raise TypeError('"testing_panel" must be the instance of '
                            '"TestingPanel"')
        self.datasets = datasets

        self.__set_execution_ui()
        self.__set_options_ui()
        self.__set_outputs_ui()
        self.__set_graphic_ui()

    def __set_execution_ui(self):
        group_box = QGroupBox('Training')
        inner_layout = QHBoxLayout()
        group_box.setLayout(inner_layout)

        self.data_selector = QComboBox()
        self.data_selector.addItems(self.datasets.keys())
        self.data_selector.setStatusTip('Select the training dataset.')
        # self.data_selector.currentIndexChanged.connect(self.__change_map)

        self.start_btn = QPushButton('Train')
        self.start_btn.setStatusTip('Start training.')
        # self.start_btn.clicked.connect(self.__run)

        self.stop_btn = QPushButton('Stop')
        self.stop_btn.setStatusTip('Force the training stop running.')
        self.stop_btn.setDisabled(True)

        inner_layout.addWidget(self.data_selector, 1)
        inner_layout.addWidget(self.start_btn)
        inner_layout.addWidget(self.stop_btn)

        self._layout.addWidget(group_box)

    def __set_options_ui(self):
        group_box = QGroupBox('Training Options')
        inner_layout = QFormLayout()
        group_box.setLayout(inner_layout)

        self.iter_times = QSpinBox()
        self.iter_times.setRange(1, 1000000)
        self.iter_times.setValue(10000)
        self.iter_times.setStatusTip('The total iterating times for training.')

        self.population_size = QSpinBox()
        self.population_size.setRange(1, 100000000)
        self.population_size.setValue(10000)
        self.population_size.setStatusTip('The population size for genetic '
                                          'algorithm.')

        self.p_crossover = QDoubleSpinBox()
        self.p_crossover.setRange(0, 1)
        self.p_crossover.setValue(0.5)
        self.p_crossover.setSingleStep(0.1)
        self.p_crossover.setStatusTip('The probability of crossover for '
                                      'genetic algorithm.')

        self.p_mutation = QDoubleSpinBox()
        self.p_mutation.setRange(0, 1)
        self.p_mutation.setValue(0.5)
        self.p_mutation.setSingleStep(0.1)
        self.p_mutation.setStatusTip('The probability of mutation for '
                                     'genetic algorithm.')

        self.nneuron = QSpinBox()
        self.nneuron.setRange(0, 10000)
        self.nneuron.setValue(4)
        self.nneuron.setStatusTip('The number of RBFN neuron.')

        inner_layout.addRow(QLabel('Iterating Times:'), self.iter_times)
        inner_layout.addRow(QLabel('Population Size:'), self.population_size)
        inner_layout.addRow(QLabel('Crossover Probability:'), self.p_crossover)
        inner_layout.addRow(QLabel('Mutation Probability:'), self.p_mutation)
        inner_layout.addRow(QLabel('Number of Neuron:'), self.nneuron)

        self._layout.addWidget(group_box)

    def __set_outputs_ui(self):
        group_box = QGroupBox('Training Details')
        inner_layout = QFormLayout()
        group_box.setLayout(inner_layout)

        self.current_iter_time = QLabel('--')
        self.current_output = QLabel('--')
        self.current_error = QLabel('--')

        self.current_iter_time.setAlignment(Qt.AlignCenter)
        self.current_output.setAlignment(Qt.AlignCenter)
        self.current_error.setAlignment(Qt.AlignCenter)

        self.current_iter_time.setStatusTip('The current iterating time of '
                                            'genetic algorithm.')
        self.current_output.setStatusTip('The current output from the RBFN.')
        self.current_error.setStatusTip('The current error from the fitting '
                                        'function.')

        inner_layout.addRow('Current Iterating Time:', self.current_iter_time)
        inner_layout.addRow('Current Output:', self.current_output)
        inner_layout.addRow('Current Error:', self.current_error)

        self._layout.addWidget(group_box)

    def __set_graphic_ui(self):
        group_box = QGroupBox('Error Line Chart:')
        inner_layout = QHBoxLayout()
        group_box.setLayout(inner_layout)

        self.err_chart = ErrorLineChart()
        self.err_chart.setStatusTip('The history of error from the fitting '
                                    ' of genetic algorithm.')

        inner_layout.addWidget(self.err_chart)
        self._layout.addWidget(group_box)
