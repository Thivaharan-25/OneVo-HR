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

### Zero Trust Architecture

- WAF + DDoS protection (Cloudflare)
- mTLS between services (when services are separated)
- All PII encrypted at rest (AES-256) and in transit (TLS 1.3)
- Input sanitization pipeline on all endpoints

### OWASP Top-10 Mitigations

| Vulnerability | Mitigation |
|:-------------|:-----------|
| Injection | Parameterized queries via EF Core; no raw SQL |
| Broken Auth | JWT RS256, refresh token rotation, MFA support — see [[auth-architecture]] |
| Sensitive Data Exposure | AES-256 encryption, PII log scrubbing — see [[data-classification]] |
| XXE | JSON-only API (no XML parsing) |
| Broken Access Control | RBAC with 80+ permissions, RLS — see [[multi-tenancy]] |
| Security Misconfiguration | Hardened defaults, HSTS, CSP headers |
| XSS | Content-Type enforcement, CSP headers |
| Insecure Deserialization | System.Text.Json with strict options |
| Known Vulnerabilities | Dependabot alerts, regular dependency updates |
| Insufficient Logging | Serilog structured logging, audit trail — see [[logging-standards]] |

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
