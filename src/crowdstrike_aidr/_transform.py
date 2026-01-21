"""Utilities for converting data structures to JSON-serializable formats."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from pydantic import BaseModel

from ._utils import is_given, is_iterable, is_list, is_mapping, is_sequence


def _transform_typeddict(data: Mapping[str, object]) -> dict[str, object]:
    """
    Transform a TypedDict-like mapping.

    Args:
        data: A `Mapping` to transform.

    Returns:
        A new dictionary with transformed values, excluding unset entries.
    """
    return {key: transform(value) for key, value in data.items() if is_given(value)}


def transform(data: object) -> object:
    """
    Transform an object into a JSON-serializable format.

    Args:
        data: The object to transform.

    Returns:
        A JSON-serializable representation of the input data.
    """
    if is_mapping(data):
        return _transform_typeddict(data)

    if isinstance(data, BaseModel):
        return data.model_dump(exclude_unset=True, mode="json")

    if (
        # list[T]
        is_list(data)
        # Iterable[T]
        or (is_iterable(data) and not isinstance(data, str))
        # Sequence[T]
        or (is_sequence(data) and not isinstance(data, str))
    ):
        # dicts are iterable, but it's an iterable on the keys, so it doesn't
        # get transformed here.
        if isinstance(data, dict):
            return cast(object, data)

        return [transform(d) for d in data]

    return data
