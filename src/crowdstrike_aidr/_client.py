from __future__ import annotations

import contextlib
import json
import time
from collections.abc import Mapping
from random import random
from typing import TYPE_CHECKING, Any, cast, get_origin, override

import httpx
from httpx import URL, Timeout
from pydantic import BaseModel

from ._constants import (
    DEFAULT_CONNECTION_LIMITS,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    INITIAL_RETRY_DELAY,
    MAX_RETRY_DELAY,
)
from ._exceptions import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    UnprocessableEntityError,
)
from ._models import FinalRequestOptions
from ._types import _T, AnyMapping, Body, Headers, NotGiven, Omit, Query, RequestOptions, ResponseT, _T_co, not_given
from ._utils import is_given, is_mapping


def make_request_options(
    *,
    query: Query | None = None,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = not_given,
) -> RequestOptions:
    options: RequestOptions = {}
    if extra_headers is not None:
        options["headers"] = extra_headers

    if extra_body is not None:
        options["extra_json"] = cast(AnyMapping, extra_body)

    if query is not None:
        options["params"] = query

    if extra_query is not None:
        options["params"] = {**options.get("params", {}), **extra_query}

    if not isinstance(timeout, NotGiven):
        options["timeout"] = timeout

    return options


def _merge_mappings(
    obj1: Mapping[_T_co, _T | Omit],
    obj2: Mapping[_T_co, _T | Omit],
) -> dict[_T_co, _T]:
    """
    Merge two mappings of the same type, removing any values that are instances
    of `Omit`.

    In cases with duplicate keys the second mapping takes precedence.
    """

    merged = {**obj1, **obj2}
    return {key: value for key, value in merged.items() if not isinstance(value, Omit)}


class BaseClient[T: httpx.Client | httpx.AsyncClient]:
    _client: T
    _service_name: str

    def __init__(
        self,
        *,
        base_url_template: str,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout: float | Timeout | None = DEFAULT_TIMEOUT,
        custom_headers: Mapping[str, str] | None = None,
        custom_query: Mapping[str, object] | None = None,
    ) -> None:
        self.max_retries = max_retries
        self.timeout = timeout
        self._base_url_template = base_url_template
        self._custom_headers = custom_headers or {}
        self._custom_query = custom_query or {}

    @property
    def auth_headers(self) -> dict[str, str]:
        return {}

    @property
    def base_url(self) -> URL:
        resolved_url = self._base_url_template.replace("{SERVICE_NAME}", self._service_name)
        return URL(resolved_url)

    @property
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
            **self.auth_headers,
            **self._custom_headers,
        }

    @property
    def default_query(self) -> dict[str, object]:
        return {**self._custom_query}

    @property
    def user_agent(self) -> str:
        return "aidr-python"

    def _build_headers(self, options: FinalRequestOptions, *, retries_taken: int = 0) -> httpx.Headers:
        custom_headers = options.headers or {}
        headers_dict = _merge_mappings(self.default_headers, custom_headers)
        return httpx.Headers(headers_dict)

    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return InternalServerError(err_msg, response=response, body=body)

        return APIStatusError(err_msg, response=response, body=body)

    def _make_status_error_from_response(
        self,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.is_closed and not response.is_stream_consumed:
            body = None
            err_msg = f"Error code: {response.status_code}"
        else:
            err_text = response.text.strip()
            body = err_text

            try:
                body = json.loads(err_text)
                err_msg = f"Error code: {response.status_code} - {body}"
            except Exception:
                err_msg = err_text or f"Error code: {response.status_code}"

        return self._make_status_error(err_msg, body=body, response=response)

    def _prepare_url(self, url: str) -> URL:
        """
        Merge a URL argument together with any 'base_url' on the client, to
        create the URL used for the outgoing request.
        """

        merge_url = URL(url)
        if merge_url.is_relative_url:
            base_url = self.base_url
            # Ensure exactly one slash separator between base and relative paths
            merge_raw_path = base_url.raw_path.rstrip(b"/") + b"/" + merge_url.raw_path.lstrip(b"/")
            return base_url.copy_with(raw_path=merge_raw_path)

        return merge_url

    def _should_retry(self, response: httpx.Response) -> bool:
        return (
            response.status_code == 408
            or response.status_code == 409
            or response.status_code == 429
            or response.status_code >= 500
        )


class _DefaultHttpxClient(httpx.Client):
    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        kwargs.setdefault("limits", DEFAULT_CONNECTION_LIMITS)
        kwargs.setdefault("follow_redirects", True)
        super().__init__(**kwargs)


if TYPE_CHECKING:
    DefaultHttpxClient = httpx.Client
    """
    An alias to `httpx.Client` that provides the same defaults that this SDK
    uses internally.

    This is useful because overriding the `http_client` with your own instance
    of `httpx.Client` will result in httpx's defaults being used, not ours.
    """
else:
    DefaultHttpxClient = _DefaultHttpxClient


class SyncHttpxClientWrapper(DefaultHttpxClient):
    def __del__(self) -> None:
        if self.is_closed:
            return

        with contextlib.suppress(Exception):
            self.close()


class SyncAPIClient(BaseClient[httpx.Client]):
    _client: httpx.Client
    _token: str

    def __init__(
        self,
        *,
        base_url_template: str,
        token: str,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout: float | Timeout = DEFAULT_TIMEOUT,
        http_client: httpx.Client | None = None,
        custom_headers: Mapping[str, str] | None = None,
        custom_query: Mapping[str, object] | None = None,
    ) -> None:
        if http_client is not None and not isinstance(http_client, httpx.Client):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError(
                f"Invalid `http_client` argument; Expected an instance of `httpx.Client` but got {type(http_client)}"
            )

        super().__init__(
            timeout=cast(Timeout, timeout),
            base_url_template=base_url_template,
            max_retries=max_retries,
            custom_headers=custom_headers,
            custom_query=custom_query,
        )

        self._token = token

        resolved_base_url = self.base_url
        self._client = http_client or SyncHttpxClientWrapper(base_url=resolved_base_url, timeout=self.timeout)

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token}"}

    def _post(
        self,
        path: str,
        *,
        cast_to: type[ResponseT],
        body: Body | None = None,
        options: RequestOptions = {},  # noqa: B006
    ) -> ResponseT:
        opts = FinalRequestOptions.construct(method="post", url=path, json_data=body, **options)
        return cast(ResponseT, self._request(cast_to, opts))

    def _request(
        self,
        cast_to: type[ResponseT],
        options: FinalRequestOptions,
    ) -> ResponseT:
        input_options = options.model_copy()
        response: httpx.Response | None = None
        max_retries = input_options.get_max_retries(self.max_retries)

        retries_taken = 0
        for retries_taken in range(max_retries + 1):
            options = input_options.model_copy()
            remaining_retries = max_retries - retries_taken
            request = self._build_request(options, retries_taken=retries_taken)

            response = None
            try:
                response = self._client.send(request)
            except httpx.TimeoutException as err:
                if remaining_retries > 0:
                    self._sleep_for_retry(retries_taken=retries_taken, max_retries=max_retries, options=input_options)
                    continue

                raise APITimeoutError(request=request) from err
            except Exception as err:
                if remaining_retries > 0:
                    self._sleep_for_retry(retries_taken=retries_taken, max_retries=max_retries, options=input_options)
                    continue

                raise APIConnectionError(request=request) from err

            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as err:  # thrown on 4xx and 5xx status code
                if remaining_retries > 0 and self._should_retry(err.response):
                    err.response.close()
                    self._sleep_for_retry(retries_taken=retries_taken, max_retries=max_retries, options=input_options)
                    continue

                if not err.response.is_closed:
                    err.response.read()

                raise self._make_status_error_from_response(err.response) from None

            break

        assert response is not None
        return self._process_response(
            cast_to=cast_to,
            options=options,
            response=response,
            retries_taken=retries_taken,
        )

    def _build_request(
        self,
        options: FinalRequestOptions,
        *,
        retries_taken: int = 0,
    ) -> httpx.Request:
        kwargs: dict[str, Any] = {}

        json_data = options.json_data
        if options.extra_json is not None:
            if json_data is None:
                json_data = cast(Body, options.extra_json)
            elif is_mapping(json_data):
                json_data = _merge_mappings(json_data, options.extra_json)
            else:
                raise RuntimeError(f"Unexpected JSON data type, {type(json_data)}, cannot merge with `extra_body`")

        headers = self._build_headers(options, retries_taken=retries_taken)
        params = _merge_mappings(self.default_query, options.params)

        prepared_url = self._prepare_url(options.url)
        is_body_allowed = options.method.lower() != "get"

        if is_body_allowed:
            if isinstance(json_data, bytes):
                kwargs["content"] = json_data
            else:
                kwargs["json"] = json_data if is_given(json_data) else None
        else:
            headers.pop("Content-Type", None)
            kwargs.pop("data", None)

        return self._client.build_request(
            headers=headers,
            timeout=self.timeout if isinstance(options.timeout, NotGiven) else options.timeout,
            method=options.method,
            url=prepared_url,
            params=cast(Mapping[str, Any], params) if params else None,
            **kwargs,
        )

    def _calculate_retry_timeout(self, remaining_retries: int, options: FinalRequestOptions) -> float:
        max_retries = options.get_max_retries(self.max_retries)
        nb_retries = min(max_retries - remaining_retries, 1000)
        sleep_seconds = min(INITIAL_RETRY_DELAY * pow(2.0, nb_retries), MAX_RETRY_DELAY)
        jitter = 1 - 0.25 * random()
        timeout = sleep_seconds * jitter
        return timeout if timeout >= 0 else 0

    def _sleep_for_retry(self, *, retries_taken: int, max_retries: int, options: FinalRequestOptions) -> None:
        remaining_retries = max_retries - retries_taken
        timeout = self._calculate_retry_timeout(remaining_retries, options)
        time.sleep(timeout)

    def _process_response(
        self,
        *,
        cast_to: type[ResponseT],
        options: FinalRequestOptions,
        response: httpx.Response,
        retries_taken: int = 0,
    ) -> ResponseT:
        origin: type[ResponseT] = get_origin(cast_to) or cast_to

        if issubclass(origin, BaseModel):
            return origin.model_validate(response.json())

        return cast(ResponseT, response.json())
