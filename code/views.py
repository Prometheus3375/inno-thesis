from typing import Generic, TypeVar, overload

T = TypeVar('T')


class ListView(Generic[T]):
    __slots__ = '_source',

    def __init__(self, source: list[T], /):
        self._source = source

    def __len__(self, /):
        return len(self._source)

    def __iter__(self, /):
        return iter(self._source)

    def __contains__(self, item: T, /):
        return item in self._source

    @overload
    def __getitem__(self, item: int, /) -> T: ...

    @overload
    def __getitem__(self, item: slice, /) -> list[T]: ...

    def __getitem__(self, item, /):
        return self._source[item]
