from math import atan2, cos, sin, sqrt
from typing import Literal, overload

from common import Real, deg, real


class PointBase:
    __slots__ = '_x', '_y'

    def __init__(self, x: float, y: float, /):
        self._x = x
        self._y = y

    @property
    def x(self, /) -> float:
        return self._x

    @property
    def y(self, /) -> float:
        return self._y

    @property
    def r2(self) -> float:
        return self.x * self.x + self.y * self.y

    @property
    def r(self, /) -> float:
        return sqrt(self.r2)

    @property
    def fi(self, /) -> float:
        return atan2(self.y, self.x)

    def _str_x(self, named: bool = True, /):
        return f'x={self.x:.2g}' if named else f'{self.x:.2g}'

    def _str_y(self, named: bool = True, /):
        return f'y={self.y:.2g}' if named else f'{self.y:.2g}'

    def _str_r(self, named: bool = True, /):
        return f'r={self.r:.2g}' if named else f'{self.r:.2g}'

    def _str_fi(self, named: bool = True, /):
        return f'φ={deg(self.fi):.0f}°' if named else f'{deg(self.fi):.0f}°'

    def __str__(self, /):
        return f'({self._str_x(False)}, {self._str_y(False)})'

    def _str_cartesian(self, /):
        return f'({self._str_x()}, {self._str_y()})'

    def _str_polar(self, /):
        return f'({self._str_r()}, {self._str_fi()})'

    def __format__(self, format_spec, /):
        if format_spec == '':
            return self.__str__()
        if format_spec == 'c':
            return self._str_cartesian()
        if format_spec == 'p':
            return self._str_polar()

        raise ValueError(f'invalid format specifier {format_spec!r} for {self.__class__.__name__}; '
                         f'allowed specifiers are \'c\' and \'p\'')

    def __repr__(self, /):
        return f'{self.__class__.__name__}({self._str_x()}, {self._str_y()})'

    @staticmethod
    def _new(x: float, y: float, /):
        raise NotImplementedError

    def copy(self, /):
        return self._new(self.x, self.y)

    def __getnewargs__(self, /):
        return self._x, self._y

    def fix(self, /) -> 'FixedPoint':
        raise NotImplementedError

    def __eq__(self, other, /):
        if isinstance(other, PointBase):
            return self.x == other.x and self.y == other.y

        return NotImplemented

    def __ne__(self, other, /):
        if isinstance(other, PointBase):
            return self.x != other.x or self.y != other.y

        return NotImplemented

    def __neg__(self, /):
        return self._new(-self.x, -self.y)

    def __pos__(self, /):
        return self.copy()

    def __abs__(self, /):
        return self.r

    def __add__(self, other, /):
        if isinstance(other, real):
            return self._new(self.x + other, self.y + other)

        if isinstance(other, PointBase):
            return self._new(self.x + other.x, self.y + other.y)

        return NotImplemented

    def __radd__(self, other, /):
        return self.__add__(other)

    def __sub__(self, other, /):
        if isinstance(other, real):
            return self._new(self.x - other, self.y - other)

        elif isinstance(other, PointBase):
            return self._new(self.x - other.x, self.y - other.y)

        return NotImplemented

    def __rsub__(self, other, /):
        if isinstance(other, real):
            return self._new(other - self.x, other - self.y)

        elif isinstance(other, PointBase):
            return self._new(other.x - self.x, other.y - self.y)

        return NotImplemented

    def __mul__(self, other, /):
        if isinstance(other, real):
            return self._new(self.x * other, self.y * other)

        if isinstance(other, PointBase):
            return self._new(self.x * other.x, self.y * other.y)

        return NotImplemented

    def __rmul__(self, other, /):
        return self.__mul__(other)

    def __truediv__(self, other, /):
        if isinstance(other, real):
            return self._new(self.x / other, self.y / other)

        if isinstance(other, self.__class__):
            return self._new(self.x / other.x, self.y / other.x)

        return NotImplemented

    def __rtruediv__(self, other, /):
        if isinstance(other, real):
            return self._new(other / self.x, other / self.y)

        if isinstance(other, self.__class__):
            return self._new(other.x / self.x, other.x / self.y)

        return NotImplemented

    def __floordiv__(self, other, /):
        if isinstance(other, real):
            return self._new(self.x // other, self.y // other)

        if isinstance(other, self.__class__):
            return self._new(self.x // other.x, self.y // other.x)

        return NotImplemented

    def __rfloordiv__(self, other, /):
        if isinstance(other, real):
            return self._new(other // self.x, other // self.y)

        if isinstance(other, self.__class__):
            return self._new(other.x // self.x, other.x // self.y)

        return NotImplemented


class FixedPoint(PointBase):
    __slots__ = '_hash', '_fi', '_r2', '_r'

    # r2 is necessary to store, because sqrt(a) * sqrt(a) != a in general

    def __init__(self, x: float, y: float, /):
        super().__init__(x, y)
        self._r2 = x * x + y * y
        self._r = sqrt(self._r2)
        self._fi = atan2(y, x)
        self._hash = hash((x, y))

    @PointBase.r2.getter
    def r2(self, /) -> float:
        return self._r2

    @PointBase.r.getter
    def r(self, /) -> float:
        return self._r

    @PointBase.fi.getter
    def fi(self, /) -> float:
        return self._fi

    @staticmethod
    def _new(x: float, y: float, /):
        return FixedPoint(x, y)

    def fix(self, /):
        return self

    def __hash__(self, /):
        return self._hash


class MutablePoint(PointBase):
    __slots__ = ()

    @PointBase.x.setter
    def x(self, value: Real, /):
        self._x = float(value)

    @PointBase.y.setter
    def y(self, value: Real, /):
        self._y = float(value)

    @PointBase.r.setter
    def r(self, r: Real, /):
        fi = self.fi
        self._x = r * cos(fi)
        self._y = r * sin(fi)

    @PointBase.fi.setter
    def fi(self, fi: Real, /):
        r = self.r
        self._x = r * cos(fi)
        self._y = r * sin(fi)

    @staticmethod
    def _new(x: float, y: float, /):
        return MutablePoint(x, y)

    def fix(self, /):
        return FixedPoint(self.x, self.y)

    def __iadd__(self, other, /):
        if isinstance(other, real):
            self._x += other
            self._y += other
            return self

        if isinstance(other, PointBase):
            self._x += other.x
            self._y += other.y
            return self

        return NotImplemented

    def __isub__(self, other, /):
        if isinstance(other, real):
            self._x -= other
            self._y -= other
            return self

        if isinstance(other, PointBase):
            self._x -= other.x
            self._y -= other.y
            return self

        return NotImplemented

    def __imul__(self, other, /):
        if isinstance(other, real):
            self._x *= other
            self._y *= other
            return self

        if isinstance(other, PointBase):
            self._x *= other.x
            self._y *= other.y
            return self

        return NotImplemented

    def __itruediv__(self, other, /):
        if isinstance(other, real):
            self._x /= other
            self._y /= other
            return self

        if isinstance(other, PointBase):
            self._x /= other.x
            self._y /= other.y
            return self

        return NotImplemented

    def __ifloordiv__(self, other, /):
        if isinstance(other, real):
            self._x //= other
            self._y //= other
            return self

        if isinstance(other, PointBase):
            self._x //= other.x
            self._y //= other.y
            return self

        return NotImplemented


class NamedPointBase(PointBase):
    __slots__ = ()  # no slots here due to inheritance conflict

    def __init__(self, name: str, x: float, y: float, /):
        super().__init__(x, y)
        # noinspection PyUnresolvedReferences,PyDunderSlots
        self._name = name

    @property
    def name(self, /) -> str:
        return self._name

    def __str__(self, /):
        return f'{self.name}({self._str_x(False)}, {self._str_y(False)})'

    def _str_cartesian(self, /):
        return f'{self.name}({self._str_x()}, {self._str_y()})'

    def _str_polar(self, /):
        return f'{self.name}({self._str_r()}, {self._str_fi()})'

    def __repr__(self, /):
        return f'{self.__class__.__name__}(name={self.name}, {self._str_x()}, {self._str_y()})'

    def __getnewargs__(self, /):
        return self._name, self._x, self._y


class NamedFixedPoint(NamedPointBase, FixedPoint):
    __slots__ = '_name',


class NamedMutablePoint(NamedPointBase, MutablePoint):
    __slots__ = '_name',


@overload
def point(x_or_r: Real, y_or_fi: Real, /, *,
          polar: bool = False) -> FixedPoint: ...


@overload
def point(x_or_r: Real, y_or_fi: Real, /, *,
          fixed: Literal[True], polar: bool = False) -> FixedPoint: ...


@overload
def point(x_or_r: Real, y_or_fi: Real, /, *,
          fixed: Literal[False], polar: bool = False) -> MutablePoint: ...


@overload
def point(x_or_r: Real, y_or_fi: Real, name: str, /, *,
          polar: bool = False) -> NamedFixedPoint: ...


@overload
def point(x_or_r: Real, y_or_fi: Real, name: str, /, *,
          fixed: Literal[True], polar: bool = False) -> NamedFixedPoint: ...


@overload
def point(x_or_r: Real, y_or_fi: Real, name: str, /, *,
          fixed: Literal[False], polar: bool = False) -> NamedMutablePoint: ...


def point(x_or_r: Real, y_or_fi: Real, name: str = None, /, *, fixed: bool = True, polar: bool = False) -> PointBase:
    if isinstance(name, str):
        if name == '':
            raise ValueError('name of a point cannot be empty')

        if not ('A' <= name[0] <= 'Z'):
            raise ValueError(f'name of a point must start with upper latin letter, got {name!r}')

        for c in name:
            if not ('A' <= c <= 'Z' or '0' <= c <= '9'):
                raise ValueError(f'name of a point must contain only upper latin letters and digits, got {name!r}')
    elif name is not None:
        raise TypeError(f'name of a point must be a string, got {type(name)}')

    if polar:
        x = x_or_r * cos(y_or_fi)
        y = x_or_r * sin(y_or_fi)
    else:
        x = float(x_or_r)
        y = float(y_or_fi)

    if fixed:
        if name:
            return NamedFixedPoint(name, x, y)

        return FixedPoint(x, y)

    else:
        if name:
            return NamedMutablePoint(name, x, y)

        return MutablePoint(x, y)
