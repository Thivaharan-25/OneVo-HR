# Security Center Userflow

## Actor

Security operator.

## Journey

1. Operator opens Security & Compliance -> Security Center.
2. Console loads session, failed login, and risk summaries.
3. Operator filters suspicious sessions or events.
4. If permitted, operator revokes a session.
5. Backend audits security query and revocation.

## APIs Used

- `GET /admin/v1/security/overview`
- `GET /admin/v1/security/sessions`
- `POST /admin/v1/security/sessions/{sessionId}/revoke`
