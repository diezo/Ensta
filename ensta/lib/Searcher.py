from abc import ABC, abstractmethod
from typing import Any, Set, Generic, TypeVar, Sequence
from dataclasses import dataclass

E = TypeVar('E')


class Predicate(ABC, Generic[E]):

    @abstractmethod
    def __call__(self, obj: E) -> bool:
        raise NotImplementedError()

    def __and__(self, predicate: 'Predicate[E]') -> 'Predicate[E]':
        return _AndPredicate((self, predicate,))


@dataclass(frozen=True)
class _AndPredicate(Predicate[E]):

    predicates: Sequence[Predicate[E]]

    def __call__(self, obj: E) -> bool:
        for predicate in self.predicates:
            if not predicate(obj):
                return False
        return True

    def __and__(self, predicate: 'Predicate[E]') -> 'Predicate[E]':
        return _AndPredicate(self.predicates + (predicate,))


@dataclass(frozen=True)
class ContainKeys(Predicate[Any]):

    keys: Set[str]

    def test(self, obj: Any) -> bool:
        if not isinstance(obj, dict):
            return False
        return self.keys.issubset(obj.keys())

    def __call__(self, obj: Any) -> bool:
        return self.test(obj)


@dataclass(frozen=True)
class MatchKeyValues(Predicate[Any]):

    key_values: dict

    def test(self, obj: dict) -> bool:
        if not isinstance(obj, dict):
            return False
        for k, v in self.key_values.items():
            if k not in obj:
                return False
            if obj[k] != v:
                return False
        return True

    def __call__(self, obj) -> bool:
        return self.test(obj)


def create_search_obj(*keys, **key_values):

    predicate = ContainKeys(set(keys)) & MatchKeyValues(dict(key_values))

    def search_obj(json_data):
        if predicate(json_data):
            yield json_data
        if isinstance(json_data, (list, tuple,)):
            for item in json_data:
                yield from search_obj(item)
        elif isinstance(json_data, dict):
            for _, v in json_data.items():
                yield from search_obj(v)

    return search_obj


search_comments = create_search_obj(**{"__typename": "XDTCommentDict"})
