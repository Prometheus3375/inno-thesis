from math import atan2, ceil, cos, degrees as deg, floor, pi as PI, radians as rad, sin, sqrt, tan
from typing import Union

real = int, float
Real = Union[int, float]

TWOPI = 2 * PI


def reduce_angle(angle: Real) -> float:
    """
    Move angle in radians to range (-π, π]
    """
    if -PI < angle <= PI:
        return angle

    n = angle / TWOPI
    n = ceil(n) if n < 0 else floor(n)
    return angle - n * TWOPI


__all__ = 'atan2', 'ceil', 'cos', 'deg', 'floor', 'PI', 'rad', 'sin', 'sqrt', 'tan', \
          'real', 'Real', 'TWOPI', 'reduce_angle'
