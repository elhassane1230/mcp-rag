# Security

## Encryption
All data is encrypted in transit with TLS 1.3 and at rest with AES-256. Encryption
keys are managed by a hardware security module and rotated annually.

## Single sign-on
Enterprise customers can enable SSO via SAML 2.0 or OIDC, integrating with providers
like Okta, Azure AD, and Google Workspace. SSO enforces your identity provider's MFA
policy.

## Audit logs
Every administrative action — key creation, permission change, data deletion — is
written to an immutable audit log. Audit logs are available via the
`/v1/audit` endpoint and can be streamed to your SIEM. Logs are retained for 2 years.

## Vulnerability disclosure
Report security issues to security@nimbus.example. Nimbus runs a bug-bounty program
and commits to acknowledging reports within 2 business days.
