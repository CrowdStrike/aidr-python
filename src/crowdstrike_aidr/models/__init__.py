from __future__ import annotations

from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, Field

__all__ = ("PangeaResponse",)


class PangeaResponse(BaseModel):
    """Pangea standard response schema"""

    request_id: str
    """
    A unique identifier assigned to each request made to the API. It is used to
    track and identify a specific request and its associated data. The
    `request_id` can be helpful for troubleshooting, auditing, and tracing the
    flow of requests within the system. It allows users to reference and
    retrieve information related to a particular request, such as the response,
    parameters, and raw data associated with that specific request.

    ```
    "request_id":"prq_x6fdiizbon6j3bsdvnpmwxsz2aan7fqd"
    ```
    """

    request_time: AwareDatetime
    """
    The timestamp indicates the exact moment when a request is made to the API.
    It represents the date and time at which the request was initiated by the
    client. The `request_time` is useful for tracking and analyzing the timing
    of requests, measuring response times, and monitoring performance metrics.
    It allows users to determine the duration between the request initiation and
    the corresponding response, aiding in the assessment of API performance and
    latency.

    ```
    "request_time":"2022-09-21T17:24:33.105Z"
    ```
    """

    response_time: AwareDatetime
    """
    Duration it takes for the API to process a request and generate a response.
    It represents the elapsed time from when the request is received by the API
    to when the corresponding response is returned to the client.

    ```
    "response_time":"2022-09-21T17:24:34.007Z"
    ```
    """

    status: Literal["Success"] | str
    """
    It represents the status or outcome of the API request made for IP
    information. It indicates the current state or condition of the request and
    provides information on the success or failure of the request.

    ```
    "status":"success"
    ```
    """

    summary: str | None = None
    """
    Provides a concise and brief overview of the purpose or primary objective of
    the API endpoint. It serves as a high-level summary or description of the
    functionality or feature offered by the endpoint.
    """

    result: object | None = None


class Error(BaseModel):
    code: Literal[
        "FieldRequired",
        "InvalidString",
        "InvalidNumber",
        "InvalidInteger",
        "InvalidObject",
        "InvalidArray",
        "InvalidNull",
        "InvalidBool",
        "BadFormat",
        "BadFormatPangeaDuration",
        "BadFormatDateTime",
        "BadFormatTime",
        "BadFormatDate",
        "BadFormatEmail",
        "BadFormatHostname",
        "BadFormatIPv4",
        "BadFormatIPv6",
        "BadFormatIPAddress",
        "BadFormatUUID",
        "BadFormatURI",
        "BadFormatURIReference",
        "BadFormatIRI",
        "BadFormatIRIReference",
        "BadFormatJSONPointer",
        "BadFormatRelativeJSONPointer",
        "BadFormatRegex",
        "BadFormatJSONPath",
        "BadFormatBase64",
        "DoesNotMatchPattern",
        "DoesNotMatchPatternProperties",
        "NotEnumMember",
        "AboveMaxLength",
        "BelowMinLength",
        "AboveMaxItems",
        "BelowMinItems",
        "NotMultipleOf",
        "NotWithinRange",
        "UnexpectedProperty",
        "InvalidPropertyName",
        "AboveMaxProperties",
        "BelowMinProperties",
        "NotContains",
        "ContainsTooMany",
        "ContainsTooFew",
        "ItemNotUnique",
        "UnexpectedAdditionalItem",
        "InvalidConst",
        "IsDependentOn",
        "IsTooBig",
        "IsTooSmall",
        "ShouldNotBeValid",
        "NoUnevaluatedItems",
        "NoUnevaluatedProperties",
        "DoesNotExist",
        "IsReadOnly",
        "CannotAddToDefault",
        "MustProvideOne",
        "MutuallyExclusive",
        "BadState",
        "InaccessibleURI",
        "ProviderDisabled",
        "ConfigProjectMismatch",
        "ConfigServiceMismatch",
        "ConfigNotExist",
    ]
    detail: str
    """
    Human readable description of the error
    """
    source: str
    """
    Path to the data source of the error
    """
    path: str | None = None
    """
    The Schema path where the error occurred
    """


class Result(BaseModel):
    errors: Annotated[list[Error], Field(min_length=1)]


class PangeaValidationErrors(BaseModel):
    result: Result
