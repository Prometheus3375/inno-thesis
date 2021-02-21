from io import StringIO
from math import atan2, ceil
from typing import Literal, Union, overload

from common import PI, Real, TWOPI, deg, real, reduce_angle
from functions import qbezeir_svg_given_middle
from .circle import CircleBase, FixedCircle
from .point import PointBase, polar


def check_arc(value: float, /):
    if not (0 < value < TWOPI):
        raise ValueError(f'arc should be in range (0°, 360°), got {deg(value):.0g}°')


class SectorBase:
    __slots__ = '_circle', '_arc', '_arm'

    def __init__(self, circle: CircleBase, arc: float, arm: float, /):
        self._circle = circle
        self._arc = arc
        self._arm = arm

    @property
    def circle(self, /):
        return self._circle

    @property
    def arc(self, /):
        return self._arc

    @property
    def start_arm(self, /):
        return self._arm

    @property
    def end_arm(self, /):
        return self._arm - self._arc

    @property
    def end_arm_reduced(self, /):
        return reduce_angle(self.end_arm)

    def __repr__(self, /):
        return (
            f'{self.__class__.__name__}('
            f'{self._circle}, '
            f'arc={deg(self._arc):.0f}°, '
            f'start_arm={deg(self._arm):.0f}°'
            f')'
        )

    def copy(self, /):
        return self.__class__(self._circle.copy(), self._arc, self._arm)

    def __getnewargs__(self, /):
        return self._circle, self._arc, self._arm

    def fix(self, /) -> 'FixedSector':
        raise NotImplementedError

    def unfix(self, /) -> 'MutableSector':
        raise NotImplementedError

    def __eq__(self, other, /):
        if isinstance(other, SectorBase):
            return self._arc == other._arc and self._arm == self._arm and self._circle == other._circle

        return NotImplemented

    def __ne__(self, other, /):
        if isinstance(other, SectorBase):
            return self._arc != other._arc or self._arm != self._arm or self._circle != other._circle

        return NotImplemented

    def is_angle_inside(self, fi: Real, /) -> bool:
        fi = reduce_angle(fi)
        start = self._arm
        end = self.end_arm_reduced
        if end > start:
            return end <= fi <= PI or -PI < fi <= start

        return end <= fi <= start

    def is_point_inside(self, p: PointBase, /) -> bool:
        # Another way https://stackoverflow.com/a/13675772

        x = p.x - self.circle.center.x
        y = p.y - self.circle.center.y
        r2 = x * x + y * y
        if r2 == 0:
            return True
        if r2 > self.circle.r2:
            return False

        return self.is_angle_inside(atan2(y, x))

    def __contains__(self, item, /):
        if isinstance(item, real):
            return self.is_angle_inside(item)

        if isinstance(item, PointBase):
            return self.is_point_inside(item)

        return False

    def as_plotly_shape(self, step_angle: Real = PI / 6, /) -> dict:
        # Simulate circle arc with quadratic Bezier curves
        center = self.circle.center
        r = self.circle.radius
        n = ceil(self.arc / step_angle) - 1
        p0 = polar(r, self._arm) + center
        path = StringIO()
        path.write(
            f'M {center.x} {center.y} '
            f'L {p0.x} {p0.y} '
        )
        arm = self.start_arm
        for _ in range(n):
            pm = polar(r, arm - step_angle / 2) + center
            arm -= step_angle
            p2 = polar(r, arm) + center
            path.write(f'{qbezeir_svg_given_middle(p0, p2, pm)} ')
            p0 = p2

        p2 = polar(r, self.end_arm) + center
        pm = polar(r, (arm + self.end_arm) / 2) + center
        path.write(f'{qbezeir_svg_given_middle(p0, p2, pm)} Z')

        return dict(
            type='path',
            path=path.getvalue()
        )


class FixedSector(SectorBase):
    __slots__ = '_hash',

    def __init__(self, circle: FixedCircle, arc: float, arm: float, /):
        super().__init__(circle, arc, arm)
        self._hash = hash(frozenset((circle, arc, arm)))

    def fix(self, /):
        return self

    def unfix(self, /):
        return MutableSector(self._circle.unfix(), self._arc, self._arm)

    def __hash__(self, /):
        return self._hash


class MutableSector(SectorBase):
    __slots__ = ()

    @property
    def arc(self, /):
        return self._arc

    @arc.setter
    def arc(self, value: Real, /):
        check_arc(value)
        self._arc = float(value)

    @property
    def start_arm(self, /):
        return self._arm

    @start_arm.setter
    def start_arm(self, value: Real, /):
        self._arm = reduce_angle(float(value))

    @property
    def end_arm(self, /):
        return self._arm - self._arc

    @end_arm.setter
    def end_arm(self, value: Real, /):
        self._arm = reduce_angle(value + self._arc)

    def fix(self, /):
        return FixedSector(self._circle.fix(), self._arc, self._arm)

    def unfix(self, /):
        return self

    def rotate(self, angle: Real, /):
        """
        Rotates the sector by the given angle clockwise
        """
        self.start_arm -= angle


@overload
def sector(circle: CircleBase, arc: Real, start_arm: Real = PI, /) -> FixedSector: ...


@overload
def sector(circle: CircleBase, arc: Real, start_arm: Real = PI, /, *, fix: Literal[True]) -> FixedSector: ...


@overload
def sector(circle: CircleBase, arc: Real, start_arm: Real = PI, /, *, fix: Literal[False]) -> MutableSector: ...


@overload
def sector(circle: CircleBase, arc: Real, start_arm: Real = PI, /, *,
           fix: bool) -> Union[FixedSector, MutableSector]: ...


def sector(circle: CircleBase, arc: Real, start_arm: Real = PI, /, *, fix: bool = True) -> SectorBase:
    check_arc(arc)
    arc = float(arc)
    start_arm = float(start_arm)

    if fix:
        return FixedSector(circle.fix(), arc, start_arm)

    return MutableSector(circle.unfix(), arc, start_arm)
