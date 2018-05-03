""" Define the contents of training panel. """

from panel import Panel
from testing_panel import TestingPanel


class TrainingPanel(Panel):

    def __init__(self, maps, datasets, testing_panel):
        super().__init__()
        if isinstance(testing_panel, TestingPanel):
            self.graphic_panel = testing_panel
        else:
            raise TypeError("'testing_panel' must be the instance of "
                            "'TestingPanel'")
        self.maps = maps
        self.datasets = datasets

        self.__set_execution_ui()
        self.__set_options_ui()
        self.__set_outputs_ui()
        self.__set_graphic_ui()
        self.__set_console_ui()

    def __set_execution_ui(self):
        pass

    def __set_options_ui(self):
        pass

    def __set_outputs_ui(self):
        pass

    def __set_graphic_ui(self):
        pass

    def __set_console_ui(self):
        pass
