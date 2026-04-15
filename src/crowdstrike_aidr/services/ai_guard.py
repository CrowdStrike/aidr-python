from __future__ import annotations

from typing import Literal

import httpx

from .._client import SyncAPIClient, make_request_options
from .._transform import transform
from .._types import Body, Headers, NotGiven, Omit, Query, not_given, omit
from ..models.ai_guard import ExtraInfo, GuardChatCompletionsResponse, UnredactResponse


class AIGuard(SyncAPIClient):
    _service_name: str = "aiguard"

    def guard_chat_completions(
        self,
        *,
        guard_input: object,
        app_id: str | Omit = omit,
        collector_instance_id: str | Omit = omit,
        event_type: Literal["input", "output", "tool_input", "tool_output", "tool_listing"] | Omit = omit,
        extra_info: ExtraInfo | Omit = omit,
        llm_provider: str | Omit = omit,
        model: str | Omit = omit,
        model_version: str | Omit = omit,
        source_ip: str | Omit = omit,
        source_location: str | Omit = omit,
        span_id: str | Omit = omit,
        tenant_id: str | Omit = omit,
        user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters
        # to the API that aren't available via kwargs. The extra values given
        # here take precedence over values defined on the client or passed to
        # this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GuardChatCompletionsResponse:
        """
        Analyze and redact content to avoid manipulation of the model, addition
        of malicious content, and other undesirable data transfers.

        Args:
          guard_input: 'messages' contains Prompt content and role array in JSON format. The `content`
              is the multimodal text or image input that will be analyzed. Additional
              properties such as 'tools' may be provided for analysis.

          app_id: Id of source application/agent

          collector_instance_id: (AIDR) collector instance id.

          event_type: (AIDR) Event Type.

          extra_info: (AIDR) Logging schema.

          llm_provider: Underlying LLM. Example: 'OpenAI'.

          model: Model used to perform the event. Example: 'gpt'.

          model_version: Model version used to perform the event. Example: '3.5'.

          source_ip: IP address of user or app or agent.

          source_location: Location of user or app or agent.

          span_id: Unique identifier for the span in distributed tracing, used
              to track and correlate AI events across the request lifecycle.

          tenant_id: For gateway-like integrations with multi-tenant support.

          user_id: User/Service account id/service account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/guard_chat_completions",
            body=transform(
                {
                    "guard_input": guard_input,
                    "app_id": app_id,
                    "collector_instance_id": collector_instance_id,
                    "event_type": event_type,
                    "extra_info": extra_info,
                    "llm_provider": llm_provider,
                    "model": model,
                    "model_version": model_version,
                    "source_ip": source_ip,
                    "source_location": source_location,
                    "span_id": span_id,
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                }
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GuardChatCompletionsResponse,
        )

    def unredact(
        self,
        *,
        fpe_context: str,
        redacted_data: object,
        # Use the following arguments if you need to pass additional parameters
        # to the API that aren't available via kwargs. The extra values given
        # here take precedence over values defined on the client or passed to
        # this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UnredactResponse:
        """
        Decrypt or unredact fpe redactions

        Args:
          fpe_context: FPE context used to decrypt and unredact data

          redacted_data: Data to unredact

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/unredact",
            body=transform(
                {
                    "fpe_context": fpe_context,
                    "redacted_data": redacted_data,
                },
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UnredactResponse,
        )
