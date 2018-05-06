import copy
import functools
import itertools
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
            self.__reproduction = self.__roulette_wheel_selection
        else:
            self.__reproduction = self.__tournament_selection

        if mean_range is None:
            mean_range = (min(min(d.i) for d in self.dataset),
                          max(max(d.i) for d in self.dataset))

        self.abort = False

        # initialize population
        data_dim = len(self.dataset[0].i)
        self.nneuron = len(self.rbfn.neurons)
        self.population = list()
        for _ in range(self.population_size):
            indiv = np.random.uniform(-1, 1, self.nneuron)
            indiv = np.append(indiv, np.random.uniform(
                *mean_range, (self.nneuron - 1) * data_dim))
            indiv = np.append(indiv, np.random.uniform(0, sd_max, self.nneuron - 1))
            self.population.append(indiv)

    def run(self):
        for i in range(self.iter_times):
            if self.abort:
                break
            self.sig_current_iter_time.emit(i)

            # calculate the fitting function
            results = self.__get_fitting_function_results()

            for r in results:
                time.sleep(0.001)
                self.sig_current_error.emit(r)
            avg_error = sum(results) / len(results)
            self.sig_avg_error.emit(avg_error)

            # reproduction
            scores = np.full_like(results, max(results) + avg_error) - results
            self.__reproduction(dict(zip(scores, self.population)))

            # crossover
            self.__crossover()

            # mutation
            #self.__mutation()

        results = self.__get_fitting_function_results()
        self.rbfn.load_model(min(zip(results, self.population))[1])
        self.sig_rbfn.emit(self.rbfn)

    @pyqtSlot()
    def stop(self):
        if self.isRunning():
            self.sig_console.emit("WARNING: User interrupts running thread. "
                                  "The thread will be stop in next iteration.")

        self.abort = True

    def __get_fitting_function_results(self):
        with mp.Pool() as pool:
            results = pool.map(functools.partial(fitting_func,
                                                 dataset=self.dataset,
                                                 rbfn=copy.deepcopy(self.rbfn)),
                               self.population)
        return np.array(results)

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

        self.population = pool

    def __tournament_selection(self, choices):
        pool = list()
        for _ in range(self.population_size):
            pool.append(
                choices[max(random.choices(list(choices.keys()), k=2))])
        self.population = pool

    def __crossover(self):
        def pairwise(iterable):
            iterator = iter(iterable)
            return zip(iterator, iterator)

        random.shuffle(self.population)
        pairs = list(map(list, pairwise(self.population)))
        for pair in pairs:
            if random.uniform(0, 1) <= self.pc:
                if bool(random.getrandbits(1)):
                    # closer
                    pair[0] = pair[0] + random.uniform(0, 1) * (pair[0] - pair[1])
                    pair[1] = pair[1] - random.uniform(0, 1) * (pair[0] - pair[1])
                else:
                    # further
                    pair[0] = pair[0] + random.uniform(0, 1) * (pair[1] - pair[0])
                    pair[1] = pair[1] - random.uniform(0, 1) * (pair[1] - pair[0])
        if len(self.population) % 2 == 1:
            last_chromosome = self.population[-1]
            self.population = list(itertools.chain.from_iterable(pairs))
            self.population.append(last_chromosome)
        else:
            self.population = list(itertools.chain.from_iterable(pairs))

    def __mutation(self):
        def random_noise():
            pass
        pass

    def __chromosome_limiter(self, chromosome):
        chromosome[:self.nneuron]

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
    return 0.5 * sum(abs(d.o - rbfn.output(d.i, antinorm=True)) for d in dataset)
