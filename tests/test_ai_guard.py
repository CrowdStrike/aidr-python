from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

from crowdstrike_aidr import AIGuard
from crowdstrike_aidr.models.ai_guard import GuardChatCompletionsResponse

from .utils import assert_matches_type

base_url_template = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


@pytest.fixture(scope="session")
def client(request: pytest.FixtureRequest) -> Iterator[AIGuard]:
    yield AIGuard(base_url_template=base_url_template)


def test_guard_chat_completions(client: AIGuard) -> None:
    response = client.guard_chat_completions(guard_input={"messages": [{"role": "user", "content": "Hello, world!"}]})
    assert_matches_type(GuardChatCompletionsResponse, response, path=["guard_chat_completions"])
