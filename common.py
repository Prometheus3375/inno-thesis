# noinspection PyUnresolvedReferences
from math import atan2, ceil, cos, degrees as deg, floor, pi as PI, radians as rad, sin, sqrt, tan
from typing import Union as _Union

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
