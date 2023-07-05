from typing import Iterable, NamedTuple, Tuple

from common import Real, TWOPI, reduce_angle
from data import CyclicTuple
from figures import Sector
from point import Point


def circular_subtraction(a1: float, a2: float) -> float:
    return a1 - a2 if a1 >= a2 else a1 - a2 + TWOPI


class Group(NamedTuple):
    start_arm: Real
    points: Tuple[Point, ...]


def find_all_groups(sector: Sector, points: Iterable[Point]) -> Iterable[Group]:
    # FIXME: fix problems when some points are duplicated
    # TODO: create special structure to hold original point, its circle projection, angle and duplicates
    # TODO: Report bug about expected type
    # TODO: create abc class with method get_location() which returns fixed point

    points = [p for p in points if sector.circle.is_point_inside(p)]
    n = len(points)
    if n == 0:
        return
    if n == 1:
        p = points[0]
        a = (p - sector.center).fi
        yield Group(reduce_angle(a + sector.arc / 2), (p,))

    angles = [(p - sector.center).fi for p in points]

    points, angles = zip(*sorted(zip(points, angles), key=lambda t: t[1], reverse=True))
    points: CyclicTuple[Point] = CyclicTuple(points)
    angles: CyclicTuple[float] = CyclicTuple(angles)

    sector.start_arm = angles[0]
    first = 0
    afterlast = 1
    # Find index of first point not inside
    while afterlast < n and sector.is_angle_inside(angles[afterlast]):
        afterlast += 1
    while True:
        yield Group(sector.start_arm, tuple(points[i] for i in points.make_slice(first, afterlast)))

        a1 = angles[first]
        an1 = angles[afterlast]
        alpha = circular_subtraction(sector.start_arm, a1)
        omega = circular_subtraction(sector.end_arm, an1)

        # Try to rotate sector by such angle that
        # only first point inside (p1) will be excluded
        # and first point not inside (pn1) will not be included
        if alpha >= omega:
            # Not possible to exclude p1 and not include pn1
            # Rotating end arm to pn1 forms a new group with the same first point
            sector.end_arm = an1
            afterlast += 1
        else:  # alpha < omega
            # It is possible to exclude p1 and not include pn1
            # Rotate start arm to p1, this action will not change group
            sector.start_arm = a1

            if points[first] is points[afterlast - 1]:
                # p1 is the only point inside
                # Rotate end arm to pn1, it will form a new group
                sector.end_arm = an1
                first = afterlast
                afterlast += 1
            else:
                gamma = circular_subtraction(a1, angles[first + 1])  # angle to second point inside
                omega = circular_subtraction(sector.end_arm, an1)  # angle to pn1 after rotation
                rho = min(gamma, omega) / 2
                sector.rotate(rho)
                first += 1

        if sector.start_arm == angles[0]:
            break
