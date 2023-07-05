from typing import Union as _Union
# noinspection PyUnresolvedReferences
from math import sqrt, pi as PI, sin, cos, tan, atan2, radians as rad, degrees as deg, floor, ceil

real = (int, float)
Real = _Union[int, float]

TWOPI = 2 * PI


def reduce_angle(angle: Real) -> float:
    """
    Move angle in radians to range (-π, π]
    """
    if -PI < angle <= PI:
        return angle

    n = angle / TWOPI
    n = floor(n) if angle < 0 else ceil(n)
    return angle - n * TWOPI
