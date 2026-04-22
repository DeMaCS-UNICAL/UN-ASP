#! /usr/bin/python3
import math

default_rho = 10
default_sigma = 10


def isNumber(x):
    return (type(x) is int or type(x) is float) and not type(x) is bool

#
# frange source taken from known pip package
# 
def frange(start, stop=None, step=1):
    """frange generates a set of floating point values over the 
    range [start, stop) with step size step    
    frange([start,] stop [, step ])"""

    if stop is None:
        for x in range(int(math.ceil(start))):
            yield x
    else:
        # create a generator expression for the index values
        indices = (i for i in range(0, int((stop - start) / step)))
        # yield results
        for i in indices:
            yield start + step * i

#
# Converts X to the nearest lower multiple of S
# 
def generalFloor(X, S):
    return math.floor(X / S) * S

#
# Converts X to the nearest upper multiple of S
# 
def generalCeil(X, S):
    return math.ceil(X / S) * S


def split_number_naive(q, rho=default_rho, sigma=default_sigma):
    retValue = []
    if not isNumber(q):
        raise ValueError(f"The value {q} cannot be casted into a number.")
    samples = frange(generalCeil(q - rho, sigma), generalFloor(q + rho, sigma) + sigma, sigma)

    for sample in samples:
        # We want closed intervals at left, and open to the right
        if sample != q + rho:
            retValue.append(sample)
    return retValue


if __name__ == "__main__":
    #print(split_number_naive(39749.2, 100.010,100.010))
    #print(split_number_naive(42533.2, 100.010, 100.010))
    print(split_number_naive(38311.200, 10, 0.10))
