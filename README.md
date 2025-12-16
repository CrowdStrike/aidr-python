# CrowdStrike AIDR Python SDK

Python SDK for CrowdStrike AIDR.

## Installation

```bash
pip install crowdstrike-aidr
```

## Requirements

Python v3.12 or greater.

## Usage

```python
from crowdstrike_aidr import AIGuard

client = AIGuard(
  base_url_template="https://api.crowdstrike.com/aidr/{SERVICE_NAME}",
  token="my API token"
)

response = client.guard_chat_completions(
    guard_input={
        "messages": [
            {"role": "user", "content": "Hello, world!"}
        ]
    }
)
```

## Timeouts

The SDK uses `httpx.Timeout` for timeout configuration. By default, requests
have a timeout of 60 seconds with a 5 second connection timeout.

You can configure timeouts in two ways:

### Client-level timeout

Set a default timeout for all requests made by the client:

```python
import httpx
from crowdstrike_aidr import AIGuard

# Using a float (total timeout in seconds).
client = AIGuard(
    base_url_template="https://api.crowdstrike.com/aidr/{SERVICE_NAME}",
    token="my API token",
    timeout=30.0,
)

# Using httpx.Timeout for more granular control.
client = AIGuard(
    base_url_template="https://api.crowdstrike.com/aidr/{SERVICE_NAME}",
    token="my API token",
    timeout=httpx.Timeout(timeout=60.0, connect=10.0),
)
```

### Request-level timeout

Override the timeout for a specific request:

```python
# Using a float (total timeout in seconds).
response = client.guard_chat_completions(
    guard_input={"messages": [...]},
    timeout=120.0
)

# Using httpx.Timeout for more granular control.
response = client.guard_chat_completions(
    guard_input={"messages": [...]},
    timeout=httpx.Timeout(timeout=120.0, connect=15.0)
)
```

## Retries

The SDK automatically retries failed requests with exponential backoff. By
default, the client will retry up to 2 times. Set `max_retries` during client
creation to change this.

```python
from crowdstrike_aidr import AIGuard

client = AIGuard(
    base_url_template="https://api.crowdstrike.com/aidr/{SERVICE_NAME}",
    max_retries=5  # Retry up to 5 times.
)
```
