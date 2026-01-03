"""Utilities for converting data structures to JSON-serializable formats."""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel

from ._utils import is_given, is_mapping


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

    return data
