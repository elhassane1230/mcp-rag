# Python SDK

## Installation
Install the SDK with `pip install nimbus-sdk`. It supports Python 3.9+.

## Quickstart
Create a client with your API key and start making calls:

    from nimbus import Client
    client = Client(api_key="nmb_...")
    client.events.emit(name="signup", properties={"plan": "team"})

## Pagination
List endpoints return a cursor. Iterate with `client.events.list(limit=100)` which
transparently follows cursors. To page manually, pass the `after` cursor from the
previous response.

## Retries
The SDK retries idempotent requests up to 3 times with exponential backoff on 429 and
5xx responses. Configure with `Client(api_key=..., max_retries=5)`. Non-idempotent
writes are never retried automatically to avoid duplicates.

## Async
An async client is available as `from nimbus.aio import AsyncClient` with the same
method surface using `await`.
