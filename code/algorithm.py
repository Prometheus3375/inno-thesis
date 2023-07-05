from collections.abc import Iterable, Iterator
from math import atan2
from typing import final

from common import TWOPI
from cyclic import CyclicList
from geometry.point import FixedPoint, PointBase
from geometry.sector import FixedSector, MutableSector, SectorBase
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


@final
class Group:
    __slots__ = '_sector', '_points', '_hash'

    def __init__(self, sector: FixedSector, aliases: Iterable[PointAlias], /):
        self._sector = sector
        points: list[PointBase] = []
        for alias in aliases:
            points += alias.aliases

        self._points = points
        ids = self.points_ids
        if len(points) != len(ids):
            raise ValueError(f'some points are repeated')

        # Groups are identical if they contain the same points
        # Sectors' arms are not important
        self._hash = hash(frozenset((sector.arc, sector.circle, ids)))

    @property
    def sector(self, /):
        return self._sector

    @property
    def points(self, /):
        return ListView(self._points)

    @property
    def points_ids(self, /):
        return frozenset(id(p) for p in self._points)

    def __eq__(self, other, /):
        if isinstance(other, Group):
            return (
                self.sector.arc == other.sector.arc and
                self.sector.circle == other.sector.circle and
                self.points_ids == other.points_ids
            )

        return NotImplemented

    def __ne__(self, other, /):
        if isinstance(other, Group):
            return (
                self.sector.arc != other.sector.arc or
                self.sector.circle != other.sector.circle or
                self.points_ids != other.points_ids
            )

        return NotImplemented

    def __hash__(self, /):
        return self._hash


def circular_subtraction(a1: float, a2: float) -> float:
    return a1 - a2 if a1 >= a2 else a1 - a2 + TWOPI


def find_all_groups(sector: SectorBase, points: Iterable[PointBase]) -> Iterator[Group]:
    # Copy sector to avoid manipulations outside
    sector = sector.copy() if isinstance(sector, MutableSector) else sector.unfix()
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
    del fi2alias, alias, p, points
    # endregion

    # region Handle trivial cases
    n = len(aliases)
    if n == 0:
        return
    if n == 1:
        a = aliases[0]
        sector.start_arm = a.fi + sector.arc / 2
        yield Group(sector.fix(), [a])
        return
    # endregion

    start_angle = aliases[0].fi
    sector.start_arm = start_angle
    first = 0
    afterlast = 1

    # Find index of first point not inside
    while afterlast < n and aliases[afterlast].fi in sector:
        afterlast += 1

    first_group = Group(sector.fix(), (aliases[i] for i in aliases.indices_between(first, afterlast)))
    yield first_group

    while True:
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

            if aliases[first] is aliases[afterlast - 1]:
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

        # Form new group
        g = Group(sector.fix(), (aliases[i] for i in aliases.indices_between(first, afterlast)))
        # If new group is identical to the first one, stop iteration
        if g == first_group:
            break

        yield g
