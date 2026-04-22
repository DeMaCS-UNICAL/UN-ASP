import unittest
from unittest.mock import patch, call

import pytest
from src import approximation


# Test to verify that frange computes the right values
def test_frange():
    # Test case 1: Basic case
    assert list(approximation.frange(0, 5, 1)) == [0.0, 1.0, 2.0, 3.0, 4.0]
    # Test case 2: Default step of 1
    assert list(approximation.frange(3, 8)) == [3.0, 4.0, 5.0, 6.0, 7.0]
    # Test case 3: Floating point step
    assert list(approximation.frange(0, 2, 0.5)) == [0.0, 0.5, 1.0, 1.5]
    # Test case 4: Start only (defaults to stop being start)
    assert list(approximation.frange(4)) == [0.0, 1.0, 2.0, 3.0]
    # Test case 5: Negative step
    assert list(approximation.frange(5, 0, -1)) == [5.0, 4.0, 3.0, 2.0, 1.0]
    # Test case 6: Zero step (should raise ValueError)
    with unittest.TestCase().assertRaises(Exception):
        list(approximation.frange(0, 5, 0))
    # Test case 7: Large step size
    assert list(approximation.frange(0, 10, 10)) == [0.0]
    # Test case 8: Start equals stop
    assert list(approximation.frange(3, 3)) == []


# Test to verify generalFloor and generalCeil
def test_approximations():
    test_cases = [
        # Format: (X, S, expected_floor, expected_ceil)
        (10, 3, 9, 12),  # Basic case
        (7, 5, 5, 10),  # Exact middle
        (15, 7, 14, 21),  # Non-divisible
        (20, 4, 20, 20),  # Divisible
        (0, 5, 0, 0),  # Zero
        (-7, 5, -10, -5),  # Negative numbers
        (8.5, 2.5, 7.5, 10.0),  # Floats
    ]

    for X, S, expected_floor, expected_ceil in test_cases:
        assert approximation.generalFloor(X, S) == expected_floor, f"Failed generalFloor({X}, {S})"
        assert approximation.generalCeil(X, S) == expected_ceil, f"Failed generalCeil({X}, {S})"


# Test to verify that split_number_set and split_number_naive return the right output
def test_split_number():
    # Test with small values for q, rho, and sigma
    assert approximation.split_number_naive(123, 10, 10) == [120, 130]

    # Test with a larger q value
    assert approximation.split_number_naive(810, 10, 10) == [800, 810]

    # Test with q = 0
    assert approximation.split_number_naive(0, 5, 2) == [-4, -2, 0, 2, 4]

    # Test with negative q value
    assert approximation.split_number_naive(-100, 50, 20) == [-140, -120, -100, -80, -60]

    # Test with a very small sigma value
    assert approximation.split_number_naive(123, 10, 0.5) == [113, 113.5, 114.0, 114.5, 115.0, 115.5, 116.0, 116.5,
                                                                  117.0, 117.5, 118.0, 118.5, 119.0, 119.5, 120.0, 120.5,
                                                                  121.0, 121.5, 122.0, 122.5, 123.0, 123.5, 124.0, 124.5,
                                                                  125.0, 125.5, 126.0, 126.5, 127.0, 127.5, 128.0, 128.5,
                                                                  129.0, 129.5, 130.0, 130.5, 131.0, 131.5, 132.0, 132.5]

    # Test with large values
    assert approximation.split_number_naive(1000000, 1000, 500) == [999000, 999500, 1000000, 1000500]


# Test to verify that String cannot be given as input to the function
def test_split_number_naive_exception():
    with pytest.raises(ValueError):
        approximation.split_number_naive("String", 5, 5)
