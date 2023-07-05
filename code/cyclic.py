from collections.abc import Collection, Iterable, Iterator, Sequence
from typing import Any, Generic, TypeVar, overload

T = TypeVar('T')
S = TypeVar('S', bound=Sequence)


def _get_slice_value(o: Any, if_none: int) -> int:
    if o is None:
        return if_none
    if isinstance(o, int):
        return o
    if (idx := getattr(o, '__index__', None)) and callable(idx) and isinstance(i := idx(), int):
        # noinspection PyUnboundLocalVariable
        return i

    raise TypeError(f'slice indices must be integers or None or have an __index__ method, got {o!r}')


class CyclicSequence(Generic[T]):
    __slots__ = ()

    def _convert_index(self, i: int, /) -> int:
        return i % len(self)

    def indices_between(self, start: int, stop: int, step: int = 1, /) -> Iterator[int]:
        if step == 0:
            raise ValueError('step cannot be zero')

        if step > 0:
            compare = int.__lt__
        else:
            compare = int.__gt__

        if compare(start, stop):
            start_idx = self._convert_index(start)
            yield start_idx
            start += step

            # yield indices until the first yielded index is met again
            while compare(start, stop) and (y := self._convert_index(start)) != start_idx:
                # noinspection PyUnboundLocalVariable
                yield y
                start += step

    def _slice_indices(self, s: slice, /) -> Iterator[int]:
        start = _get_slice_value(s.start, 0)
        stop = _get_slice_value(s.stop, len(self))
        step = _get_slice_value(s.step, 1)
        return self.indices_between(start, stop, step)

    def _check_emptiness(self, /):
        if len(self) == 0:
            raise IndexError(f'{self.__class__.__name__} is empty')

    @overload
    def __getitem__(self, index: int, /) -> T: ...

    @overload
    def __getitem__(self: S, indices: slice, /) -> S: ...

    def __getitem__(self, item, /):
        self._check_emptiness()

        if isinstance(item, int):
            return super().__getitem__(self._convert_index(item))

        if isinstance(item, slice):
            getitem = super().__getitem__
            # noinspection PyArgumentList
            return self.__class__(getitem(i) for i in self._slice_indices(item))

        raise TypeError(f'{self.__class__.__name__} indices must be integers or slices, '
                        f'not {item.__class__.__name__}')

    def index(self, value: T, start: int = 0, stop: int = None) -> int:
        if stop is None:
            stop = len(self)

        if len(self) != 0:
            getitem = super().__getitem__
            for i in self.indices_between(start, stop):
                v = getitem(i)
                if v is value or v == value:
                    return i

        raise ValueError(f'{value!r} is not in {self.__class__.__name__}')


class MutableCyclicSequence(CyclicSequence[T]):
    __slots__ = ()

    @overload
    def __setitem__(self, index: int, value: T, /): ...

    @overload
    def __setitem__(self, indices: slice, values: Iterable[T], /): ...

    def __setitem__(self, item, value, /):
        self._check_emptiness()

        if isinstance(item, int):
            super().__setitem__(self._convert_index(item), value)
        elif isinstance(item, slice):
            indices = tuple(self._slice_indices(item))
            setitem = super().__setitem__
            if not isinstance(value, Collection):
                value = tuple(value)

            if len(indices) != len(value):
                raise ValueError(f'slice and value have different lengths, {len(indices)} and {len(value)}')

            for i, v in zip(indices, value):
                setitem(i, v)
        else:
            raise TypeError(f'{self.__class__.__name__} indices must be integers or slices, '
                            f'not {item.__class__.__name__}')

    @overload
    def __delitem__(self, index: int, /): ...

    @overload
    def __delitem__(self, indices: slice, /): ...

    def __delitem__(self, item, /):
        self._check_emptiness()

        if isinstance(item, int):
            super().__delitem__(self._convert_index(item))
        elif isinstance(item, slice):
            indices = set(self._slice_indices(item))
            delitem = super().__delitem__
            for i in range(len(self) - 1, -1, -1):
                if i not in indices:
                    delitem(i)
        else:
            raise TypeError(f'{self.__class__.__name__} indices must be integers or slices, '
                            f'not {item.__class__.__name__}')


class CyclicTuple(CyclicSequence, tuple):
    __slots__ = ()


class CyclicList(MutableCyclicSequence, list):
    __slots__ = ()
