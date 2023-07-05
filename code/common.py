from math import ceil, degrees, floor, pi, radians
from typing import Union

real = int, float
Real = Union[int, float]

PI = pi
TWOPI = 2 * PI

deg = degrees
rad = radians


def reduce_angle(angle: Real) -> float:
    """
    Move angle in radians to range (-π, π]
    """
    if -PI < angle <= PI:
        return angle

    n = angle / TWOPI
    n = ceil(n) if n < 0 else floor(n)
    return angle - n * TWOPI


__all__ = 'real', 'Real', 'PI', 'TWOPI', 'deg', 'rad', 'reduce_angle'
