from typing import Union, overload

from common import Real
from geometry.point import PointBase


def binomial_coefficients(degree: int, /) -> list[int]:
    if degree < 0:
        raise ValueError(f'degree must be non-negative, got {degree}')
    if degree == 0:
        return [1]
    if degree == 1:
        return [1, 1]
    previous = [1, 1]
    for d in range(2, degree + 1):
        current = [1]
        for i in range(1, d):
            current.append(previous[i - 1] + previous[i])
        current.append(1)
        previous = current
    return previous


@overload
def bezier(t: Real, /, *values: Real) -> Real: ...


@overload
def bezier(t: Real, /, *values: Union[Real, PointBase]) -> PointBase: ...


def bezier(t: Real, /, *values: Union[Real, PointBase]) -> Union[Real, PointBase]:
    if not (0 <= t <= 1):
        raise ValueError(f'parameter must be in range [0, 1], got {t}')

    n = len(values) - 1
    if n < 1:
        raise ValueError(f'number of control points must be greater than 1, got {n + 1}')

    mt = 1 - t
    w = binomial_coefficients(n)
    ans = 0
    for i, v in enumerate(values):
        ans += v * (t ** i) * (mt ** (n - i)) * w[i]

    return ans


def qbezeir_svg_given_middle(p0: PointBase, p2: PointBase, pm: PointBase, /) -> str:
    p1 = (pm - p0 / 4 - p2 / 4) * 2
    return f'Q {p1.x} {p1.y} {p2.x} {p2.y}'
