# Authentication

Nimbus supports three authentication methods: API keys, OAuth 2.0, and short-lived
service tokens.

## API keys
API keys are the simplest way to authenticate. Create one from the dashboard under
Settings → API Keys. Each key is scoped to a single project and carries a set of
permissions (read, write, admin). Pass the key in the `Authorization` header as
`Bearer nmb_...`.

## Rotating credentials
For security, every API key should be rotated at least every 90 days. To rotate a
key without downtime, create a new key, deploy it to your services, verify traffic,
then revoke the old key. Nimbus keeps a revoked key valid for a 24-hour grace
period so in-flight requests are not dropped. Rotation can be automated with the
`nimbus keys rotate` CLI command or the `/v1/keys/rotate` endpoint.

## OAuth 2.0
For user-facing applications, use the OAuth 2.0 authorization-code flow. Register a
redirect URI, obtain an authorization code, then exchange it for an access token and
a refresh token. Access tokens expire after 1 hour; use the refresh token to obtain
a new one.

## Service tokens
Service tokens are short-lived (15 minutes) JWTs minted for machine-to-machine
calls. They are the recommended method for production workloads because a leaked
token expires quickly.
