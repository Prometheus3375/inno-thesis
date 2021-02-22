from collections.abc import Iterable, Iterator
from math import atan2
from typing import NamedTuple, final

from common import TWOPI
from cyclic import CyclicList
from geometry.point import FixedPoint, PointBase
from geometry.sector import FixedSector, MutableSector
from views import ListView


@final
class PointAlias(FixedPoint):
    __slots__ = '_aliases', '_fi'

    def __init__(self, x: float, y: float, /):
        super().__init__(x, y)
        self._fi = atan2(y, x)
        self._aliases: list[PointBase] = []

    @property
    def fi(self, /):
        return self._fi

    @property
    def aliases(self, /):
        return ListView(self._aliases)

    def alias(self, p: PointBase, /):
        self._aliases.append(p)

    def __lt__(self, other, /):
        if isinstance(other, PointAlias):
            return self._fi < other._fi

        return NotImplemented


class Group(NamedTuple):
    sector: FixedSector
    points: ListView[PointBase]

    @classmethod
    def form(cls, sector: FixedSector, aliases: Iterable[PointAlias]):
        points = []
        for alias in aliases:
            points += alias.aliases

        return cls(sector, ListView(points))


def circular_subtraction(a1: float, a2: float) -> float:
    return a1 - a2 if a1 >= a2 else a1 - a2 + TWOPI


def find_all_groups(sector: MutableSector, points: Iterable[PointBase]) -> Iterator[Group]:
    # Remove points outside circle
    points = [p for p in points if p in sector.circle]

    # region Alias points
    center = sector.circle.center
    fi2alias = {}
    for p in points:
        po = p - center
        alias = fi2alias.get(po.fi)
        if alias is None:
            alias = PointAlias(po.x, po.y)
            fi2alias[alias.fi] = alias

        alias.alias(p)

    aliases = CyclicList(sorted(fi2alias.values(), reverse=True))
    del fi2alias, alias, p
    # endregion

    # region Handle trivial cases
    n = len(aliases)
    if n == 0:
        return
    if n == 1:
        a = aliases[0]
        sector.start_arm = a.fi + sector.arc / 2
        yield Group.form(sector.fix(), [a])
        return
    # endregion

    start_angle = aliases[0].fi
    sector.start_arm = start_angle
    first = 0
    afterlast = 1

    # Find index of first point not inside
    while afterlast < n and aliases[afterlast].fi in sector:
        afterlast += 1

    while True:
        yield Group.form(sector.fix(), (aliases[i] for i in aliases.indices_between(first, afterlast)))

        prev_angle = sector.start_arm

        p1 = aliases[first]
        pn1 = aliases[afterlast]
        alpha = circular_subtraction(sector.start_arm, p1.fi)
        omega = circular_subtraction(sector.end_arm, pn1.fi)

        # Try to rotate sector by such angle that
        # only first point inside (p1) will be excluded
        # and first point not inside (pn1) will not be included
        if alpha >= omega:
            # Not possible to exclude p1 and not include pn1
            # Rotating end arm to pn1 forms a new group with the same first point
            sector.end_arm = pn1.fi
            afterlast += 1
        else:  # alpha < omega
            # It is possible to exclude p1 and not include pn1
            # Rotate start arm to p1, this action will not change group
            sector.start_arm = p1.fi

            if points[first] is points[afterlast - 1]:
                # p1 is the only point inside
                # Rotate end arm to pn1, it will form a new group
                sector.end_arm = pn1.fi
                first = afterlast
                afterlast += 1
            else:
                gamma = circular_subtraction(p1.fi, aliases[first + 1].fi)  # angle to second point inside
                omega = circular_subtraction(sector.end_arm, pn1.fi)  # angle to pn1 after rotation
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
