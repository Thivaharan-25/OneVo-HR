# Compliance: ONEVO

## GDPR (UK) Compliance

| Requirement | Implementation |
|:------------|:--------------|
| Lawful basis for processing | `consent_records` table tracking consent type, version, timestamp |
| Data minimization | Only collect necessary PII; JSONB preferences for optional data |
| Storage limitation | `retention_policies` table with automated cleanup via Hangfire |
| Right to access | `compliance_exports` with full data export |
| Right to erasure | Anonymization service + legal hold check |
| Right to portability | JSON/CSV export via compliance endpoints |
| Data breach notification | Audit log monitoring + incident response runbook |
| Privacy by design | 4-layer tenant isolation, PII encryption, log scrubbing |

## PDPA (Sri Lanka) Compliance

| Requirement | Implementation |
|:------------|:--------------|
| Consent | Explicit consent capture before processing |
| Data residency | Configurable per tenant; APAC region (Singapore) available |
| Biometric data | Consent required before enrollment (`biometric_enrollments.consent_given`) |
| Cross-border transfer | Compliance framework field in `retention_policies` |

## Security Measures

## Microsoft Teams Communication Data

Microsoft Teams sync imports and exports workplace communication data through Microsoft Graph. This requires explicit tenant enablement, Microsoft admin consent, and user account linking before ONEVO can read or send Teams messages.

| Requirement | Implementation |
|:------------|:---------------|
| Tenant consent | Tenant admin enables Microsoft Teams integration and approves Graph scopes |
| User account linking | Each user links their Teams account before ONEVO sends messages as/for that user |
| Data minimization | Import only linked workspace/channel/chat messages; do not import unrelated Teams content |
| Transparency | Workspace admins see sync status, missing linked members, and existing Team member differences before linking |
| Retention | Synced Teams messages follow chat retention, legal hold, and compliance export rules |
| Legal hold | Teams-synced messages must be included when a chat/channel/workspace legal hold is active |
| Access control | ONEVO RBAC and workspace/channel membership checks apply before showing synced Teams content |

Meeting transcripts and AI meeting summaries are not part of Teams chat/group sync unless separately documented and consented.

### Zero Trust Architecture

- WAF + DDoS protection (Cloudflare)
- mTLS between services (when services are separated)
- All PII encrypted at rest (AES-256) and in transit (TLS 1.3)
- Input sanitization pipeline on all endpoints

### OWASP Top-10 Mitigations

| Vulnerability | Mitigation |
|:-------------|:-----------|
| Injection | Parameterized queries via EF Core; no raw SQL |
| Broken Auth | BFF cookie sessions, backend-held JWT/refresh rotation, MFA support â€” see [[security/auth-architecture\|Auth Architecture]] |
| Sensitive Data Exposure | AES-256 encryption, PII log scrubbing â€” see [[security/data-classification\|Data Classification]] |
| XXE | JSON-only API (no XML parsing) |
| Broken Access Control | RBAC with 80+ permissions, RLS â€” see [[infrastructure/multi-tenancy\|Multi Tenancy]] |
| Security Misconfiguration | Hardened defaults, HSTS, CSP headers |
| XSS | Content-Type enforcement, CSP headers |
| Insecure Deserialization | System.Text.Json with strict options |
| Known Vulnerabilities | Dependabot alerts, regular dependency updates |
| Insufficient Logging | Serilog structured logging, audit trail â€” see [[code-standards/logging-standards\|Logging Standards]] |

### Security Headers

```csharp
app.UseHsts();
app.Use(async (context, next) =>
{
    context.Response.Headers.Append("X-Content-Type-Options", "nosniff");
    context.Response.Headers.Append("X-Frame-Options", "DENY");
    context.Response.Headers.Append("X-XSS-Protection", "0"); // Rely on CSP instead
    context.Response.Headers.Append("Content-Security-Policy", "default-src 'none'");
    context.Response.Headers.Append("Referrer-Policy", "strict-origin-when-cross-origin");
    context.Response.Headers.Append("Permissions-Policy", "camera=(), microphone=(), geolocation=()");
    await next();
});
```

## Related

- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]

