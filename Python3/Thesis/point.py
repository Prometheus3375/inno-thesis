from common import *


class Point:
    def __init__(self, x: Real = 0., y: Real = 0.):
        self.x = x
        self.y = y

    @property
    def fi(self) -> float:
        return atan2(self.y, self.x)

    @fi.setter
    def fi(self, fi: Real):
        r = self.r
        self.x = r * cos(fi)
        self.y = r * sin(fi)

    @property
    def r2(self) -> float:
        return self.x * self.x + self.y * self.y

    @r2.setter
    def r2(self, r: Real):
        self.r = sqrt(r)

    @property
    def r(self) -> float:
        return sqrt(self.r2)

    @r.setter
    def r(self, r: Real):
        fi = self.fi
        self.x = r * cos(fi)
        self.y = r * sin(fi)

    def __repr__(self):
        return f'(x={self.x:.2g}, y={self.y:.2g})'

    @property
    def C(self) -> str:
        return self.__repr__()

    @property
    def P(self) -> str:
        return f'(r={self.r:.2g}, φ={deg(self.fi):.0f}°)'

    def copy(self):
        return self.__class__(self.x, self.y)

    clone = copy

    @classmethod
    def polar(cls, r: Real = 0., fi: Real = 0.):
        return cls(r * cos(fi), r * sin(fi))

    def __iadd__(self, other):
        if isinstance(other, real):
            self.x += other
            self.y += other
        elif isinstance(other, self.__class__):
            self.x += other.x
            self.y += other.y
        else:
            raise TypeError(f'Addition is not defined between {self.__class__} and {other.__class__} instances')
        return self

    def __add__(self, other):
        return self.copy().__iadd__(other)

    def __radd__(self, other):
        return self.__add__(other)

    def __isub__(self, other):
        if isinstance(other, real):
            self.x -= other
            self.y -= other
        elif isinstance(other, self.__class__):
            self.x -= other.x
            self.y -= other.y
        else:
            raise TypeError(f'Subtraction is not defined between {self.__class__} and {other.__class__} instances')
        return self

    def __sub__(self, other):
        return self.copy().__isub__(other)

    def __rsub__(self, other):
        if isinstance(other, real):
            return self.__class__(other - self.x, other - self.y)
        if isinstance(other, self.__class__):
            return other.__sub__(self)

        raise TypeError(f'Subtraction is not defined between {self.__class__} and {other.__class__} instances')

    def __imul__(self, other):
        if isinstance(other, real):
            self.x *= other
            self.y *= other
        elif isinstance(other, self.__class__):
            self.x *= other.x
            self.y *= other.y
        else:
            raise TypeError(f'Multiplication is not defined between {self.__class__} and {other.__class__} instances')
        return self

    def __mul__(self, other):
        return self.copy().__imul__(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __itruediv__(self, other):
        if isinstance(other, real):
            self.x /= other
            self.y /= other
        elif isinstance(other, self.__class__):
            self.x /= other.x
            self.y /= other.y
        else:
            raise TypeError(f'Division is not defined between {self.__class__} and {other.__class__} instances')
        return self

    def __truediv__(self, other):
        return self.copy().__itruediv__(other)

    def __rtruediv__(self, other):
        if isinstance(other, real):
            return self.__class__(other / self.x, other / self.y)
        if isinstance(other, self.__class__):
            return other.__truediv__(self)

        raise TypeError(f'Division is not defined between {self.__class__} and {other.__class__} instances')

    def __ifloordiv__(self, other):
        if isinstance(other, real):
            self.x //= other
            self.y //= other
        elif isinstance(other, self.__class__):
            self.x //= other.x
            self.y //= other.y
        else:
            raise TypeError(f'Floor division is not defined between {self.__class__} and {other.__class__} instances')
        return self

    def __floordiv__(self, other):
        return self.copy().__ifloordiv__(other)

    def __rfloordiv__(self, other):
        if isinstance(other, real):
            return self.__class__(other // self.x, other // self.y)
        if isinstance(other, self.__class__):
            return other.__floordiv__(self)

        raise TypeError(f'Floor division is not defined between {self.__class__} and {other.__class__} instances')

    def __neg__(self):
        return self.__class__(-self.x, -self.y)

    def __pos__(self):
        return self.copy()

    def __abs__(self):
        return self.r

    def __eq__(self, other: 'Point'):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other: 'Point'):
        return self.x != other.x or self.y != other.y
