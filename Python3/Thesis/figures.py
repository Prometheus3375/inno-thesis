from common import *
from functions import qbezeir_svg_given_middle
from point import Point


class Circle:
    def __init__(self, center: Point, radius: Real):
        self._center = center
        self.radius = radius

    @property
    def center(self):
        return self._center

    @property
    def r(self):
        return self.radius

    def nudge(self, *, x: Real, y: Real):
        self._center.x += x
        self._center.y += y

    def move(self, p: Point):
        self._center.x = p.x
        self._center.y = p.y

    def __repr__(self):
        return f'{self.__class__.__name__}(center={self._center}, r={self.radius:.2g})'

    def __eq__(self, other: 'Circle'):
        return self.radius == other.radius and self._center == other._center

    def __ne__(self, other: 'Circle'):
        return self.radius != other.radius or self._center != other._center

    def is_point_inside(self, p: Point) -> bool:
        return (p - self.center).r2 <= self.radius * self.radius

    def as_plotly_shape(self) -> dict:
        r = self.radius
        c = self._center
        return dict(
            type='circle',
            x0=c.x - r,
            y0=c.y - r,
            x1=c.x + r,
            y1=c.y + r,
        )


class Sector:
    def __init__(self, circle: Circle, arc_size: Real, start_arm: Real = PI):
        self.circle = circle
        self._arc = arc_size
        self._start_arm = start_arm

    @property
    def arc(self):
        return self._arc

    @arc.setter
    def arc(self, value: Real):
        if not (0 < value < TWOPI):
            raise ValueError(f'Arc should be in range (0°, 360°), got {deg(value):.0g}°')
        self._arc = value

    @property
    def start_arm(self):
        return self._start_arm

    @start_arm.setter
    def start_arm(self, value: Real):
        self._start_arm = reduce_angle(value)

    @property
    def end_arm(self):
        return self._start_arm - self._arc

    @property
    def end_arm_reduced(self):
        return reduce_angle(self.end_arm)

    @end_arm.setter
    def end_arm(self, value: Real):
        self.start_arm = value + self._arc

    @property
    def r(self):
        return self.circle.radius

    radius = r

    @property
    def center(self):
        return self.circle.center

    @radius.setter
    def radius(self, value: Real):
        self.circle.radius = value

    def rotate(self, angle: Real):
        """
        Rotates the sector by the given angle clockwise
        """
        self.start_arm -= angle

    def __eq__(self, other: 'Sector'):
        return self._arc == other._arc and self._start_arm == self._start_arm and self.circle == other.circle

    def __ne__(self, other: 'Sector'):
        return self._arc != other._arc or self._start_arm != self._start_arm or self.circle != other.circle

    def is_point_inside(self, p: Point) -> bool:
        # Another way https://stackoverflow.com/a/13675772

        p = p - self.center
        if p.r2 > self.r ** 2:
            return False
        if p.r2 == 0:
            return True

        start = self.start_arm
        end = self.end_arm_reduced
        fi = p.fi
        if end > start:
            return end <= fi <= PI or -PI < fi <= start

        return end <= fi <= start

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'{self.circle}, '
            f'arc={deg(self._arc):.0f}°, '
            f'start_arm={deg(self._start_arm):.0f}°'
            f')'
        )

    def as_plotly_shape(self, step_angle: Real = PI / 6) -> dict:
        # Simulate circle ark with quadratic Bezier curves
        r = self.r
        n = ceil(self.arc / step_angle) - 1
        p0 = Point.polar(r, self.start_arm)
        path = (
            f'M {self.center.x} {self.center.y} '
            f'L {p0.x} {p0.y} '
        )
        arm = self.start_arm
        for _ in range(n):
            pm = Point.polar(r, arm - step_angle / 2)
            arm -= step_angle
            p2 = Point.polar(r, arm)
            path = f'{path} {qbezeir_svg_given_middle(p0, p2, pm)}'
            p0 = p2

        p2 = Point.polar(r, self.end_arm)
        pm = Point.polar(r, (arm + self.end_arm) / 2)
        path = f'{path} {qbezeir_svg_given_middle(p0, p2, pm)} Z'

        return dict(
            type='path',
            path=path
        )
