# Compliance: ONEVO

## GDPR (UK) Compliance

| Requirement | Implementation |
|:------------|:--------------|
| Lawful basis for processing | Versioned legal/privacy acceptance records track terms, notices, consent type, version, timestamp, source, and user context |
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
| Consent and notice | Explicit consent or acknowledgement captured before sensitive/conditional processing |
| Data residency | Configurable per tenant; APAC region (Singapore) available |
| Biometric data | Consent required before enrollment (`biometric_enrollments.consent_given`) |
| Cross-border transfer | Compliance framework field in `retention_policies` |

## Security Measures

## Microsoft Teams Communication Data

Microsoft Teams sync imports and exports workplace communication data through Microsoft Graph. This requires explicit tenant enablement, Microsoft admin consent, and user account linking before ONEVO can read or send Teams messages.

| Requirement | Implementation |
|:------------|:---------------|
| Tenant consent | Tenant admin enables Microsoft Teams integration and approves Graph scopes |


### Zero Trust Architecture

- WAF + DDoS protection (Cloudflare)
- mTLS between services (when services are separated)
- All PII encrypted at rest (AES-256) and in transit (TLS 1.3)
- Input sanitization pipeline on all endpoints

### OWASP Top-10 Mitigations

| Vulnerability | Mitigation |
|:-------------|:-----------|
| Injection | Parameterized queries via EF Core; no raw SQL |
| Broken Auth | BFF cookie sessions, backend-held JWT/refresh rotation, MFA support - see [[security/auth-architecture\|Auth Architecture]] |
| Sensitive Data Exposure | AES-256 encryption, PII log scrubbing - see [[security/data-classification\|Data Classification]] |
| XXE | JSON-only API (no XML parsing) |
| Broken Access Control | RBAC with 80+ permissions, RLS - see [[infrastructure/multi-tenancy\|Multi Tenancy]] |
| Security Misconfiguration | Hardened defaults, HSTS, CSP headers |
| XSS | Content-Type enforcement, CSP headers |
| Insecure Deserialization | System.Text.Json with strict options |
| Known Vulnerabilities | Dependabot alerts, regular dependency updates |
| Insufficient Logging | Serilog structured logging, audit trail - see [[code-standards/logging-standards\|Logging Standards]] |

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
- [[Userflow/Auth-Access/gdpr-consent|Legal & Privacy Acceptance]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]

