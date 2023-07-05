from collections.abc import Iterable, Iterator
from typing import Generic, TypeVar, final

from geometry.point import PointBase

P = TypeVar('P', bound=PointBase, covariant=True)


@final
class PointWrapper(Generic[P]):
    __slots__ = '_point', '_hash'

    def __init__(self, point: P, /):
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

    @classmethod
    def wrap(cls, points: Iterable[P]) -> Iterator['PointWrapper[P]']:
        return (cls(p) for p in points)

    @staticmethod
    def unwrap(wrapped: Iterable['PointWrapper[P]']) -> Iterator[P]:
        return (pw.p for pw in wrapped)
