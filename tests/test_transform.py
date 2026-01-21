from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from crowdstrike_aidr._transform import transform


class Foo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: str | None = None
    content: str


def test_pydantic_list() -> None:
    result = transform({"things": [Foo(role="user", content="foo"), Foo(role="user", content="bar")]})
    assert result == {"things": [{"role": "user", "content": "foo"}, {"role": "user", "content": "bar"}]}
