# Webhooks

## Configuring endpoints
Register a webhook URL in Settings → Webhooks and choose which events to subscribe
to (for example `event.created`, `invoice.paid`). Nimbus sends a POST with a JSON
payload to your endpoint.

## Verifying signatures
Every webhook includes an `X-Nimbus-Signature` header containing an HMAC-SHA256 of
the raw request body, signed with your webhook secret. Always verify this signature
before trusting the payload to prevent spoofing. Reject requests where the signature
does not match.

## Retries and idempotency
If your endpoint does not return a 2xx within 5 seconds, Nimbus retries delivery with
exponential backoff for up to 24 hours. Each delivery carries a unique
`X-Nimbus-Delivery-Id`; use it to deduplicate, since at-least-once delivery means an
event may arrive more than once.
