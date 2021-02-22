from typing import final

from geometry.point import PointBase


@final
class PointWrapper:
    __slots__ = '_point', '_hash'

    def __init__(self, point: PointBase, /):
        self._point = point
        self._hash = hash(id(point))

    @property
    def p(self, /):
        return self._point

    def __getnewargs__(self, /):
        return self._point,

    def __str__(self, /):
        return f'{self.__class__.__name__}({self._point})'

    def __repr__(self, /):
        return f'{self.__class__.__name__}({self._point!r}, id={id(self._point)})'

    def __eq__(self, other, /):
        if isinstance(other, PointWrapper):
            return self._point is other._point

        return NotImplemented

    def __ne__(self, other, /):
        if isinstance(other, PointWrapper):
            return self._point is not other._point

        return NotImplemented

    def __hash__(self, /):
        return self._hash
