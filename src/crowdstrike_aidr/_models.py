from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Required,
    TypedDict,
    TypeGuard,
    Unpack,
    final,
    get_args,
    get_origin,
)

from httpx import Timeout
from pydantic import BaseModel, ConfigDict

from ._types import AnyMapping, Body, Headers, NotGiven, Query
from ._utils import is_union, strip_not_given


def is_basemodel(type_: type) -> bool:
    """
    Returns whether or not the given type is either a `BaseModel` or a union of
    `BaseModel`.
    """

    if is_union(type_):
        return any(is_basemodel(variant) for variant in get_args(type_))

    return is_basemodel_type(type_)


def is_basemodel_type(type_: type) -> TypeGuard[type[BaseModel]]:
    origin = get_origin(type_) or type_
    if not inspect.isclass(origin):
        return False
    return issubclass(origin, BaseModel)


class FinalRequestOptionsInput(TypedDict, total=False):
    method: Required[str]
    url: Required[str]
    params: Query
    headers: Headers
    max_retries: int
    timeout: float | Timeout | None
    json_data: Body
    extra_json: AnyMapping
    follow_redirects: bool


@final
class FinalRequestOptions(BaseModel):
    method: str
    url: str
    params: Query = {}
    headers: Headers | NotGiven = NotGiven()
    max_retries: int | NotGiven = NotGiven()
    timeout: float | Timeout | None | NotGiven = NotGiven()
    post_parser: Callable[[Any], Any] | NotGiven = NotGiven()
    follow_redirects: bool | None = None

    json_data: Body | None = None
    extra_json: AnyMapping | None = None

    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    def get_max_retries(self, max_retries: int) -> int:
        if isinstance(self.max_retries, NotGiven):
            return max_retries
        return self.max_retries

    @classmethod
    def construct(  # type: ignore
        cls,
        _fields_set: set[str] | None = None,
        **values: Unpack[FinalRequestOptionsInput],
    ) -> FinalRequestOptions:
        kwargs: dict[str, Any] = {key: strip_not_given(value) for key, value in values.items()}

        return super().model_construct(_fields_set, **kwargs)

    if not TYPE_CHECKING:
        model_construct = construct
