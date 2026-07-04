# Rate limits

Nimbus enforces per-project rate limits to protect the platform.

## Limits by plan
- Free: 10 requests/second.
- Team: 100 requests/second.
- Enterprise: negotiated, typically 1000+ requests/second.

## Behaviour when throttled
When you exceed the limit, the API returns HTTP 429 with a `Retry-After` header
indicating how many seconds to wait. Rate limits use a token-bucket algorithm with a
burst allowance of 2x the sustained rate. Implement exponential backoff with jitter
to recover gracefully. Rate limits are separate from billing quotas: hitting a rate
limit is temporary throttling, whereas exceeding a quota triggers overage billing.
