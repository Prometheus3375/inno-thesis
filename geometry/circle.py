from common import Real
from .point import FixedPoint, PointBase


class CircleBase:
    __slots__ = '_center', '_radius'

    def __init__(self, center: PointBase, radius: float, /):
        self._center = center
        self._set_radius(radius)

    @property
    def center(self, /):
        return self._center

    def _set_radius(self, value: float, /):
        if value <= 0:
            raise ValueError(f'radius must be positive, got {value}')

        self._radius = value

    @property
    def radius(self, /):
        return self._radius

    def __repr__(self, /):
        return f'{self.__class__.__name__}(center={self.center}, r={self.radius:.2g})'

    def copy(self, /):
        return self.__class__(self.center.copy(), self.radius)

    def __getnewargs__(self, /):
        return self.center, self.radius

    def fix(self, /) -> 'FixedCircle':
        raise NotImplementedError

    def __eq__(self, other, /):
        if isinstance(other, CircleBase):
            return self.radius == other.radius and self.center == other.center

        return NotImplemented

    def __ne__(self, other, /):
        if isinstance(other, CircleBase):
            return self.radius != other.radius or self.center != other.center

        return NotImplemented

    def is_point_inside(self, p: PointBase, /) -> bool:
        x = p.x - self.center.x
        y = p.y - self.center.y
        return (x * x + y * y) <= self.radius * self.radius

    def __contains__(self, item: PointBase, /):
        return self.is_point_inside(item)

    def as_plotly_shape(self, /) -> dict:
        r = self.radius
        c = self.center
        return dict(
            type='circle',
            x0=c.x - r,
            y0=c.y - r,
            x1=c.x + r,
            y1=c.y + r,
        )


class FixedCircle(CircleBase):
    __slots__ = '_hash',

    def __init__(self, center: FixedPoint, radius: float, /):
        super().__init__(center, radius)
        self._hash = hash(frozenset((center, radius)))

    def fix(self, /):
        return self

    def __hash__(self, /):
        return self._hash


def circle(center: PointBase, radius: Real, /):
    return FixedCircle(center.fix(), float(radius))
