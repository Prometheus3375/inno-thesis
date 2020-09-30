from typing import Any, Iterable, List, MutableSequence, Tuple, TypeVar, Generic, Union, overload

_T = TypeVar('_T')


class CyclicList(MutableSequence, Generic[_T]):
    def __init__(self, iterable: Iterable = ()):
        self._data = list(iterable)

    def _convert_index(self, i: int) -> int:
        l = len(self)
        if l == 0:
            return i

        return i % l

    def make_slice(self, start: int = 0, stop: int = None, step: int = 1) -> Iterable[int]:
        if stop is None:
            stop = len(self)
        if step > 0:
            compare = int.__lt__
        else:
            compare = int.__gt__

        while compare(start, stop):
            yield self._convert_index(start)
            start += step

    @staticmethod
    def _get_slice_val(val: Any, if_none: int) -> int:
        if val is None:
            return if_none

        if isinstance(val, int):
            return val

        if hasattr(val, '__index__'):
            idx = getattr(val, '__index__')
            if callable(idx):
                idx = idx()

            if isinstance(idx, int):
                return idx

        raise TypeError(
            f'slice indices must be integers or None or have an __index__ method, got {val} of type {type(val)}'
        )

    def _convert_slice(self, s: slice) -> Iterable[int]:
        return self.make_slice(
            self._get_slice_val(s.start, 0),
            self._get_slice_val(s.stop, len(self)),
            self._get_slice_val(s.step, 1),
        )

    def __iter__(self):
        # Overwrite provided method to avoid infinite loop
        return iter(self._data)

    def __reversed__(self):
        # Overwrite provided method for speed-up
        return reversed(self._data)

    def index(self, value: _T, start: int = 0, end: int = None) -> int:
        # Overwrite provided method to avoid infinite loop, for speed-up, and for correct behavior
        slice_ = set(self.make_slice(start, end))
        for i in slice_:
            if self._data[i] is value or self._data[i] == value:
                return i

        raise ValueError(f'Value {value} of type {type(value)} is not in list')

    def append(self, value: _T):
        # Overwrite provided method for correct behavior
        self._data.append(value)

    def extend(self, values: Iterable[_T]):
        # Overwrite provided method for speed-up
        self._data.extend(values)

    def clear(self):
        # Overwrite provided method for speed-up
        self._data = []

    def insert(self, index: int, value: _T):
        self._data.insert(self._convert_index(index), value)

    @overload
    def __getitem__(self, i: int) -> _T:
        ...

    @overload
    def __getitem__(self, s: slice) -> 'CyclicList[_T]':
        ...

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._data[self._convert_index(item)]

        if isinstance(item, slice):
            return self.__class__(self._data[i] for i in self._convert_slice(item))

        raise TypeError(f'list indices must be integers or slices, not {type(item)}')

    @overload
    def __setitem__(self, i: int, v: _T):
        ...

    @overload
    def __setitem__(self, s: slice, v: _T):
        ...

    @overload
    def __setitem__(self, s: slice, v: Iterable[_T]):
        ...

    def __setitem__(self, item, value):
        if isinstance(item, int):
            self._data[self._convert_index(item)] = value
        elif isinstance(item, slice):
            item = self._convert_slice(item)
            if isinstance(value, Iterable):
                for i, v in zip(item, value):
                    self._data[i] = v
            else:
                for i in item:
                    self._data[i] = value
        else:
            raise TypeError(f'list indices must be integers or slices, not {type(item)}')

    @overload
    def __delitem__(self, i: int):
        ...

    @overload
    def __delitem__(self, i: slice):
        ...

    def __delitem__(self, item):
        if isinstance(item, int):
            del self._data[self._convert_index(item)]
        elif isinstance(item, slice):
            item = set(self._convert_slice(item))
            self._data = [v for i, v in enumerate(self._data) if i not in item]
        else:
            raise TypeError(f'list indices must be integers or slices, not {type(item)}')

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self):
        return f'{self.__class__.__name__}{self._data}'
