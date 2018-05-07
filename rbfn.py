import math
import random

import numpy as np


class RBFN(object):
    def __init__(self, nneuron, mean_range, sd_max=1):
        self.neurons = [Neuron(sd=random.uniform(0, sd_max),
                               mean_range=mean_range) for j in range(nneuron)]
        self.neurons.insert(0, Neuron(is_threshold=True))

    def output(self, data, antinorm=False):
        data = np.array(data)
        for neuron in self.neurons:
            neuron.input_data(data)
        res = sum(n.output for n in self.neurons)
        if antinorm:
            return self.__antinormalize(res)
        return res

    def load_model(self, params):
        """Load every parameters into the RBFN model.

        Args:
            params (list of floats): Every parameters of the RBFN. The spec is:

            | Threshold SW|     SWs     |     Means          |      SDs          |
            |-------------|-------------|--------------------|-------------------|
            |`params[0]`  |`params[1:n]`|`params[n:-(n - 1)]`|`params[-(n - 1):]`|

                where `n` is # of neurons.
        """

        nneuron = len(self.neurons)
        self.neurons[0].sw = params[0]
        weights = params[1:nneuron]
        means = params[nneuron:-(nneuron - 1)]
        sds = params[-(nneuron - 1):]
        data_dim = int(len(means) / (nneuron - 1))
        for idx, neuron in enumerate(self.neurons[1:]):
            neuron.sw = weights[idx]
            neuron.mean = np.array(means[idx * data_dim:(idx + 1) * data_dim])
            neuron.sd = sds[idx]

    @staticmethod
    def __antinormalize(value):
        if value < -1:
            return -40
        if value > 1:
            return 40
        return value * 40


class Neuron(object):
    def __init__(self, mean=None, sd=random.uniform(0, 1),
                 is_threshold=False, mean_range=None):
        """The neuron for RBFN.

        Args:
            mean (numpy.ndarray, optional): Defaults to None. The mean of
                activation function.
            sd (numpy.ndarray, optional): Defaults to random.uniform(0, 1). The
                standard deviation of activation function.
            is_threshold (bool, optional): Defaults to False. If this neuron is
                the threshold.
            mean_range (tuple of floats, optional): Defaults to (-1, 1). The
                range of mean for the random generation of activation function.
        """

        if mean_range is None:
            self.mean_range = (-1, 1)
        else:
            self.mean_range = mean_range

        self.mean = mean
        self.sd = sd  # standard deviation
        self.is_threshold = is_threshold
        self.sw = random.uniform(-1, 1)  # synaptic weight
        self.__input_data = None
        self.output = None

    def input_data(self, data):
        """Feed the input data.

        Args:
            data (numpy.ndarray): The input data.
        """

        self.__input_data = data
        if self.is_threshold:
            self.output = self.sw
        else:
            if self.mean is None:
                self.mean = np.random.uniform(*self.mean_range, size=len(data))
            self.output = self.__get_output(self.__input_data)

    def __get_output(self, data):
        if self.sd <= 0:
            return 0
        return self.sw * math.exp(
            (data - self.mean).dot(data - self.mean) / (-2 * self.sd**2))
