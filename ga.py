import copy
import functools
import multiprocessing as mp
import random
import time

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
import numpy as np

from rbfn import RBFN
from main import TrainingData  # for pickling in concurrent.futures


class GA(QThread):
    sig_console = pyqtSignal(str)
    sig_current_iter_time = pyqtSignal(int)
    sig_current_error = pyqtSignal(float)
    sig_avg_error = pyqtSignal(float)
    sig_rbfn = pyqtSignal(RBFN)

    def __init__(self, iter_times, population_size, reproduction_method, pc, pm,
                 rbfn, dataset, mean_range=None, sd_max=1):
        super().__init__()
        self.iter_times = iter_times
        self.population_size = population_size
        self.pc = pc
        self.pm = pm
        self.rbfn = rbfn
        self.dataset = dataset

        if reproduction_method == 'rw':
            self.reproduction = self.__roulette_wheel_selection
        else:
            self.reproduction = self.__tournament_selection

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

            ### calculate the fitting function
            with mp.Pool() as pool:
                results = pool.map(functools.partial(fitting_func,
                                                     dataset=self.dataset,
                                                     rbfn=copy.deepcopy(self.rbfn)),
                                   self.population)

            for r in results:
                time.sleep(0.001)
                self.sig_current_error.emit(r)
            results = np.array(results)
            avg_error = sum(results) / len(results)
            self.sig_avg_error.emit(avg_error)

            ### reproduction
            scores = np.full_like(results, max(results) + avg_error) - results
            crossover_pool = self.reproduction(dict(zip(scores, self.population)))

            self.population = crossover_pool

            ### crossover

            ### mutation

        print(time.time() - st)
        self.sig_rbfn.emit(self.rbfn)

    @pyqtSlot()
    def stop(self):
        if self.isRunning():
            self.sig_console.emit("WARNING: User interrupts running thread. "
                                  "The thread will be stop in next iteration.")

        self.abort = True

    def __roulette_wheel_selection(self, choices):
        def weighted_random_choice(choices):
            pick = random.uniform(0, sum(choices))
            current = 0
            for score, chromosome in choices.items():
                current += score
                if current > pick:
                    return chromosome

        pool = list()
        for _ in range(self.population_size):
            pool.append(weighted_random_choice(choices))

        return pool

    def __tournament_selection(self, choices):
        pool = list()
        for _ in range(self.population_size):
            pool.append(choices[max(random.choices(list(choices.keys()), k=2))])
        return pool


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
