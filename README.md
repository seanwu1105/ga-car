# Car Control Simulator Based on Genetic Algorithm

A sandbox practice for the genetic algorithm.

![preview](https://i.imgur.com/2VrKxAT.gif)

## Objective

Use genetic algorithm to find the best RBFN parameters, which input is the distances detected from car radar and output is the angle of wheel.

### Objective Function

Minimize the `err`:

``` python
err = (1 / N) * sum(abs(d.expected_output - RBFN(d.input)) for d in training_dataset)
```

`N` is the total number of training data.

### Chromosome

The chromosome is an `1 * (1 + NumOfRbfnNeuron + NumOfRbfnNeuron * InputDataDim + NumOfRbfnNeuron)` numpy array which is also the every parameters in RBFN. The spec of it is:

|   Threshold SW  |       SWs       |          Means         |          SDs          |
|:---------------:|:---------------:|:----------------------:|----------------------:|
|`chromosome[0]`  |`chromosome[1:n]`|`chromosome[n:-(n - 1)]`|`chromosome[-(n - 1):]`|

Where `n` is the # of RBFN neuron.

### Score in Selection of Genetic Algorithm

The score (affinity) of each chromosome is defined:

``` python
average_err = sum(errs) / len(errs)

scores = np.full_like(errs, max(errs) + average_err) - errs
# amplify the winner with `score_amplifier`
scores = np.power(scores, score_amplifier)
```

`errs` is the list containing all `err` of chromosome in the population.

## Installation

1. Download this project

```
git clone https://gitlab.com/GLaDOS1105/ga-car.git
```

2. Change directory to the root of the project

```
cd ga-car/
```

3. Run with Python interpreter

```
python3 main.py
```

## Training Data Format

|        Input (Distances)       |Output (Wheel Angle)|
|:------------------------------:|:------------------:|
|`22.0000000 8.4852814 8.4852814`|    `-16.0709664`   |

``` python
# Front_Distance Right_Distance Left_Distance Wheel_Angle

22.0000000 8.4852814 8.4852814 -16.0709664
21.1292288 9.3920089 7.7989045 -14.7971418
20.3973643 24.4555821 7.2000902 16.2304876
19.1995799 25.0357595 7.5129743 16.0825385
18.1744869 42.5622911 8.0705896 15.5075777
```

## Add Customized Map Cases

### The data location

The data location is `/data`. The application will load every files with `*.txt` extension automatically after the execution.

### Example Format

```
0,0,90  // the starting position and angle of car (x, y, degree)
18,40   // the top-left coordinate of the ending area
30,37   // the bottom-right coordinate of the ending area
-6,-3   // the first point for the wall in map
-6,22
18,22
18,50
30,50
30,10
6,10
6,-6
-6,-3   // the last point for the wall in map
```

Every coordinates between the fourth and last line are the corner point of the walls in map.

## Dependency

* [numpy](http://www.numpy.org/)

```
pip3 install numpy
```

* [matplotlib](https://matplotlib.org/)

```
pip3 install matplotlib
```

* [PyQt5](https://riverbankcomputing.com/software/pyqt/intro)

```
pip3 install pyqt5
```

* [PyQtChart5](https://www.riverbankcomputing.com/software/pyqtchart/intro)

```
pip3 install PyQtChart
```
