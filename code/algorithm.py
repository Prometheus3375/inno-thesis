from collections.abc import Iterable, Iterator
from typing import NamedTuple

from common import Real, TWOPI, reduce_angle
from cyclic import CyclicTuple
from geometry.point import PointBase as Point
from geometry.sector import MutableSector


def circular_subtraction(a1: float, a2: float) -> float:
    return a1 - a2 if a1 >= a2 else a1 - a2 + TWOPI


class Group(NamedTuple):
    start_arm: Real
    points: tuple[Point, ...]


def find_all_groups(sector: MutableSector, points: Iterable[Point]) -> Iterator[Group]:
    # FIXME: fix problems when some points are duplicated
    # TODO: create special structure to hold original point, its circle projection, angle and duplicates

    points = [p for p in points if sector.circle.is_point_inside(p)]
    n = len(points)
    if n == 0:
        return
    if n == 1:
        p = points[0]
        a = (p - sector.circle.center).fi
        yield Group(reduce_angle(a + sector.arc / 2), (p,))
        return

    angles = [(p - sector.circle.center).fi for p in points]

    points, angles = zip(*sorted(zip(points, angles), key=lambda t: t[1], reverse=True))
    points = CyclicTuple(points)
    angles = CyclicTuple(angles)

    start_angle = angles[0]
    sector.start_arm = start_angle
    first = 0
    afterlast = 1
    # Find index of first point not inside
    while afterlast < n and sector.is_angle_inside(angles[afterlast]):
        afterlast += 1
    while True:
        yield Group(sector.start_arm, tuple(points[i] for i in points.indices_between(first, afterlast)))

        prev_angle = sector.start_arm

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

        curr_angle = sector.start_arm
        # For cases when before rotation start arm was in 3rd quarter (-π, -π/2]
        # and after rotation in 2nd quarter [π/2, π]
        if curr_angle > prev_angle:
            prev_angle += TWOPI

        # If before iteration start arm was bigger than start angle
        # and after iteration not bigger than start angle,
        # then break the iteration
        if curr_angle <= start_angle < prev_angle:
            break
