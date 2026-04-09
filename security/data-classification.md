# Data Classification: ONEVO

## PII Inventory

### Critical PII (Encrypted at Rest — AES-256)

| Table | Column | Data Type | Contains |
|:------|:-------|:----------|:---------|
| `employee_bank_details` | `account_number_encrypted` | bytea | Bank account numbers |
| `sso_providers` | `client_id_encrypted` | bytea | SSO client IDs |
| `sso_providers` | `client_secret_encrypted` | bytea | SSO client secrets |
| `hardware_terminals` | `api_key_encrypted` | bytea | Terminal API keys |
| `integration_connections` | `credentials_encrypted` | bytea | Integration credentials |
| `notification_channels` | `credentials_encrypted` | jsonb (encrypted) | Channel provider credentials |
| `biometric_devices` | `api_key_encrypted` | bytea | Biometric terminal API keys |

### Restricted Data (Workforce Intelligence)

| Table | Column/Data | Classification | Retention | Notes |
|:------|:-----------|:---------------|:----------|:------|
| `screenshots` | Screenshot files (blob storage) | **RESTRICTED** | Per tenant policy (default 30 days) | Never store in database. Never log content. |
| `verification_records` | Verification photos (blob storage) | **RESTRICTED** | Configurable (default 30 days) | Temporary — auto-deleted by retention job |
| `application_usage` | `window_title_hash` | **RESTRICTED** | SHA-256 hash only — never store raw titles | Raw titles may contain sensitive business data |
| `activity_snapshots` | Activity data | **CONFIDENTIAL** | 90 days | Log counts only, never content |
| `activity_raw_buffer` | Raw agent payload | **CONFIDENTIAL** | 48 hours | Auto-purged daily |

### Sensitive PII (Protected by RLS + Access Control)

| Table | Column | Contains | Log Scrubbing |
|:------|:-------|:---------|:-------------|
| `users` | `email` | User email addresses | Scrubbed in logs |
| `employees` | `first_name`, `last_name` | Employee names | Allowed in audit logs |
| `employee_emergency_contacts` | `phone` | Phone numbers | Scrubbed in logs |
| `employee_addresses` | All address fields | Home addresses | Scrubbed in logs |
| `employee_dependents` | `first_name`, `last_name`, `date_of_birth` | Family member info | Scrubbed in logs |
| `user_sessions` | `ip_address` | User IP addresses | Scrubbed in logs |

### Serilog PII Scrubbing

```csharp
// Configured in Program.cs
Log.Logger = new LoggerConfiguration()
    .Destructure.ByTransforming<Employee>(e => new { e.Id, e.TenantId, Name = "***" })
    .Enrich.With(new PiiPropertyScrubber()) // Scrubs email, phone patterns
    .Enrich.With(new RegexScrubber(new[]
    {
        (@"[\w.-]+@[\w.-]+\.\w+", "***@***.***"),           // Email
        (@"eyJ[\w-]+\.eyJ[\w-]+\.[\w-]+", "***JWT***"),      // JWT tokens
        (@"\b\d{9,18}\b", "***ACCOUNT***"),                   // Bank accounts
        (@"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "***PHONE***")    // Phone numbers
    }))
    .CreateLogger();
```

## Data Retention

| Data Category | Retention | Action on Expiry | Compliance |
|:-------------|:----------|:----------------|:-----------|
| Active employee data | While employed + 7 years | Archive then delete | GDPR + Labor Law |
| Audit logs | 7 years | Partition archival | Compliance |
| Biometric events | 2 years | Delete | PDPA |
| Session data | 30 days after logout | Delete | Security |
| Notification records | 1 year | Delete | Housekeeping |
| File records | Depends on context | Delete with parent entity | GDPR |
| Activity raw buffer | 48 hours | Partition drop (daily) | Performance |
| Activity snapshots | 90 days | Partition drop (monthly) | Performance |
| Activity daily summaries | 2 years | Delete | Reporting |
| Screenshots | Per tenant policy (default 30 days) | Delete from blob + metadata | Privacy |
| Verification photos | Per tenant policy (default 30 days) | Delete from blob + metadata | Privacy |
| Agent health logs | 30 days | Delete | Housekeeping |

Managed via `retention_policies` table and Hangfire daily cleanup job. See [[security/compliance|Compliance]] for full GDPR requirements.

## GDPR Data Subject Rights

| Right | Implementation |
|:------|:--------------|
| Right to Access | `compliance_exports` — generate full data export for a user |
| Right to Erasure | Anonymization of PII fields + deletion of non-required data |
| Right to Rectification | Standard CRUD update endpoints |
| Right to Portability | Export in JSON/CSV format via `compliance_exports` |
| Right to Object | `consent_records` — withdraw consent for specific processing |

### Legal Holds

`legal_holds` table prevents deletion of data under legal proceedings:

```csharp
public async Task<bool> CanDeleteAsync(string resourceType, Guid resourceId, CancellationToken ct)
{
    var hasHold = await _context.LegalHolds
        .AnyAsync(h => h.ResourceType == resourceType 
            && h.ResourceId == resourceId 
            && h.ReleasedAt == null, ct);
    
    return !hasHold; // Cannot delete if under legal hold
}
```

## Related

- [[security/auth-architecture|Auth Architecture]]
- [[modules/configuration/retention-policies/overview|Retention Policies]]
- [[modules/activity-monitoring/screenshots/overview|Screenshots]]
- [[modules/identity-verification/photo-capture|Photo Capture]]
- [[security/compliance|Compliance]]
- [[code-standards/logging-standards|Logging Standards]]
