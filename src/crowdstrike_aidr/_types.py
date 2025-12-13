from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from typing import TYPE_CHECKING, Any, Literal, Protocol, SupportsIndex, TypedDict, TypeVar, overload, override

from httpx import Response, Timeout
from pydantic import BaseModel

Query = Mapping[str, object]
Body = object
AnyMapping = Mapping[str, object]
_T = TypeVar("_T")
_T_co = TypeVar("_T_co", covariant=True)

if TYPE_CHECKING:
    NoneType: type[None]
else:
    NoneType = type(None)


class RequestOptions(TypedDict, total=False):
    headers: Headers
    max_retries: int
    timeout: float | Timeout | None
    params: Query
    extra_json: AnyMapping
    follow_redirects: bool


# Sentinel class used until PEP 0661 is accepted
class NotGiven:
    """
    For parameters with a meaningful None value, we need to distinguish between
    the user explicitly passing None, and the user not passing the parameter at
    all.

    User code shouldn't need to use not_given directly.

    For example:

    ```py
    def create(timeout: Timeout | None | NotGiven = not_given): ...


    create(timeout=1)  # 1s timeout
    create(timeout=None)  # No timeout
    create()  # Default timeout behavior
    ```
    """

    def __bool__(self) -> Literal[False]:
        return False

    @override
    def __repr__(self) -> str:
        return "NOT_GIVEN"


not_given = NotGiven()


class Omit:
    """
    To explicitly omit something from being sent in a request, use `omit`.
    """

    def __bool__(self) -> Literal[False]:
        return False


omit = Omit()

Headers = Mapping[str, str | Omit]

ResponseT = TypeVar(
    "ResponseT",
    bound=object | str | None | BaseModel | list[Any] | dict[str, Any] | Response,
)

if TYPE_CHECKING:

    class SequenceNotStr(Protocol[_T_co]):
        @overload
        def __getitem__(self, index: SupportsIndex, /) -> _T_co: ...
        @overload
        def __getitem__(self, index: slice, /) -> Sequence[_T_co]: ...
        def __contains__(self, value: object, /) -> bool: ...
        def __len__(self) -> int: ...
        def __iter__(self) -> Iterator[_T_co]: ...
        def index(self, value: Any, start: int = 0, stop: int = ..., /) -> int: ...
        def count(self, value: Any, /) -> int: ...
        def __reversed__(self) -> Iterator[_T_co]: ...
else:
    SequenceNotStr = Sequence
