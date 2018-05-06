import concurrent.futures
import copy
import functools
import time
import multiprocessing as mp

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
import numpy as np

from rbfn import RBFN
from main import TrainingData  # for pickling in concurrent.futures


class GA(QThread):
    sig_console = pyqtSignal(str)
    sig_current_iter_time = pyqtSignal(int)
    sig_current_error = pyqtSignal(float)
    sig_rbfn = pyqtSignal(RBFN)

    def __init__(self, iter_times, population_size, pc, pm, rbfn,
                 dataset, mean_range=None, sd_max=1):
        super().__init__()
        self.iter_times = iter_times
        self.population_size = population_size
        self.pc = pc
        self.pm = pm
        self.rbfn = rbfn
        self.dataset = dataset

        if mean_range is None:
            mean_range = (min(min(d.i) for d in self.dataset),
                          max(max(d.i) for d in self.dataset))

        self.abort = False

        # initialize population
        data_dim = len(self.dataset[0].i)
        nneuron = len(self.rbfn.neurons)
        self.population = list()
        for _ in range(self.population_size):
            indiv = np.random.uniform(-1, 1, nneuron)
            indiv = np.append(indiv, np.random.uniform(
                *mean_range, (nneuron - 1) * data_dim))
            indiv = np.append(indiv, np.random.uniform(0, sd_max, nneuron - 1))
            self.population.append(indiv)

    def run(self):
        st = time.time()
        for i in range(self.iter_times):
            if self.abort:
                break
            self.sig_current_iter_time.emit(i)

            with mp.Pool() as pool:
                results = pool.map(functools.partial(fitting_func,
                                                     dataset=self.dataset,
                                                     rbfn=copy.deepcopy(self.rbfn)),
                                   self.population)
                for r in results:
                    self.sig_current_error.emit(r)

        print(time.time() - st)
        self.sig_rbfn.emit(self.rbfn)

    @pyqtSlot()
    def stop(self):
        if self.isRunning():
            self.sig_console.emit("WARNING: User interrupts running thread. "
                                  "The thread will be stop in next iteration.")

        self.abort = True


def fitting_func(indiv, dataset, rbfn):
    """Calculate the error function (fitting function) for each individual.
    This function is specially designed to be pickable for multiprocessing.

    Args:
        indiv (list of floats): The individual which is the parameters of RBFN
            model.
        dataset (list of TrainingData): The training dataset.
        rbfn (RBFN): The RBFN model which must be deep copied for different
            parameters in output calculation.

    Returns:
        float: The result of fitting function.
    """

    rbfn.load_model(indiv)
    return 0.5 * sum((d.o - rbfn.output(d.i, antinorm=True))**2 for d in dataset)
