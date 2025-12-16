from __future__ import annotations

import typing
from collections.abc import Mapping
from typing import Annotated, Any, TypeGuard, Union, cast, get_args, get_origin, overload

import typing_extensions
from typing_extensions import TypeIs

from ._types import NotGiven, Omit


def is_given[T](obj: T | NotGiven | Omit) -> TypeGuard[T]:
    return not isinstance(obj, NotGiven) and not isinstance(obj, Omit)


def is_mapping(obj: object) -> TypeGuard[Mapping[str, object]]:
    return isinstance(obj, Mapping)


@overload
def strip_not_given(obj: None) -> None: ...


@overload
def strip_not_given[K, V](obj: Mapping[K, V | NotGiven]) -> dict[K, V]: ...


@overload
def strip_not_given(obj: object) -> object: ...


def strip_not_given(obj: object | None) -> object:
    """
    Remove all top-level keys where their values are instances of `NotGiven`.
    """

    if obj is None:
        return None

    if not is_mapping(obj):
        return obj

    return {key: value for key, value in obj.items() if not isinstance(value, NotGiven)}


def is_union(tp: type | None) -> bool:
    import types

    return tp is Union or tp is types.UnionType


def extract_type_arg(typ: type, index: int) -> type:
    args = get_args(typ)
    try:
        return cast(type, args[index])
    except IndexError as err:
        raise RuntimeError(f"Expected type {typ} to have a type argument at index {index} but it did not") from err


def is_annotated_type(typ: type) -> bool:
    return get_origin(typ) == Annotated


def is_type_alias_type(tp: Any, /) -> TypeIs[typing_extensions.TypeAliasType]:
    return isinstance(tp, (typing_extensions.TypeAliasType, typing.TypeAliasType))
