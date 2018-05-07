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
    sig_iter_error = pyqtSignal(float, float)
    sig_rbfn = pyqtSignal(RBFN)

    def __init__(self, iter_times, population_size, reproduction_method, pc, pm,
                 mutation_scale, rbfn, dataset, mean_range=None, sd_max=1,
                 is_multicore=True):
        super().__init__()
        self.abort = False
        self.iter_times = iter_times
        self.population_size = population_size
        self.pc = pc
        self.pm = pm
        self.mutation_scale = mutation_scale
        self.rbfn = rbfn
        self.dataset = dataset
        self.mean_range = mean_range
        self.sd_max = sd_max
        self.is_multicore = is_multicore

        if reproduction_method == 'rw':
            self.__reproduction = self.__roulette_wheel_selection
        else:
            self.__reproduction = self.__tournament_selection

        if self.mean_range is None:
            self.mean_range = (min(min(d.i) for d in self.dataset),
                               max(max(d.i) for d in self.dataset))

        # initialize population
        self.data_dim = len(self.dataset[0].i)
        self.nneuron = len(self.rbfn.neurons)
        self.population = list()
        for _ in range(self.population_size):
            self.population.append(self.__create_chromosome())

    def run(self):
        for i in range(self.iter_times):
            if self.abort:
                break
            self.sig_current_iter_time.emit(i)

            # calculate the fitting function
            results = self.__get_fitting_function_results()

            self.__show_results(results)

            # reproduction
            avg_error = sum(results) / len(results)
            scores = np.full_like(results, max(results) + avg_error) - results
            self.__reproduction(dict(zip(scores, self.population)))

            # crossover
            self.__crossover()

            # mutation
            self.__mutation()

        self.sig_console.emit('Selecting the best chromosome...')
        results = self.__get_fitting_function_results()
        self.__show_results(results)
        best_chromosome = min(zip(results, self.population), key=lambda s: s[0])
        self.sig_console.emit('The least error: %d' % best_chromosome[0])
        self.rbfn.load_model(best_chromosome[1])
        self.sig_rbfn.emit(self.rbfn)

    @pyqtSlot()
    def stop(self):
        if self.isRunning():
            self.sig_console.emit("WARNING: User interrupts running thread. "
                                  "The thread will be stop in next iteration. "
                                  "Please wait a second...")

        self.abort = True

    def __create_chromosome(self):
        chromosome = np.random.uniform(-1, 1, self.nneuron)
        chromosome = np.append(chromosome, np.random.uniform(
            *self.mean_range, (self.nneuron - 1) * self.data_dim))
        return np.append(chromosome, np.random.uniform(
            0, self.sd_max, self.nneuron - 1))

    def __get_fitting_function_results(self):
        if self.is_multicore:
            with mp.Pool() as pool:
                results = pool.map(functools.partial(fitting_func,
                                                    dataset=self.dataset,
                                                    rbfn=copy.deepcopy(self.rbfn)),
                                self.population)
        else:
            results = list()
            for chromosome in self.population:
                results.append(fitting_func(chromosome, self.dataset, self.rbfn))
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
                    pair[0] = self.__chromosome_limiter(
                        pair[0] + random.uniform(0, 1) * (pair[0] - pair[1]))
                    pair[1] = self.__chromosome_limiter(
                        pair[1] - random.uniform(0, 1) * (pair[0] - pair[1]))
                else:
                    # further
                    pair[0] = self.__chromosome_limiter(
                        pair[0] + random.uniform(0, 1) * (pair[1] - pair[0]))
                    pair[1] = self.__chromosome_limiter(
                        pair[1] - random.uniform(0, 1) * (pair[1] - pair[0]))
        if len(self.population) % 2 == 1:
            last_chromosome = self.population[-1]
            self.population = list(itertools.chain.from_iterable(pairs))
            self.population.append(last_chromosome)
        else:
            self.population = list(itertools.chain.from_iterable(pairs))

    def __mutation(self):
        for idx, _ in enumerate(self.population):
            if random.uniform(0, 1) <= self.pm:
                self.population[idx] = self.__chromosome_limiter(
                    self.population[idx] + self.mutation_scale * self.__create_chromosome())

    def __chromosome_limiter(self, chromosome):
        np.clip(chromosome[:self.nneuron], -1,
                1, out=chromosome[:self.nneuron])
        np.clip(chromosome[-(self.nneuron - 1):], 0.0001,
                None, out=chromosome[-(self.nneuron - 1):])
        return chromosome

    def __show_results(self, results):
        for res in results:
            time.sleep(0.001)
            self.sig_current_error.emit(res)
        self.sig_iter_error.emit(sum(results) / len(results), min(results))

def fitting_func(chromosome, dataset, rbfn):
    """Calculate the error function (fitting function) for each chromosome.
    This function is specially designed to be pickable for multiprocessing.

    Args:
        chromosome (list of floats): The chromosome which is the parameters of
            RBFN model.
        dataset (list of TrainingData): The training dataset.
        rbfn (RBFN): The RBFN model which must be deep copied for different
            parameters in output calculation.

    Returns:
        float: The result of fitting function.
    """

    rbfn.load_model(chromosome)
    return sum(abs(d.o - rbfn.output(d.i, antinorm=True)) for d in dataset)
