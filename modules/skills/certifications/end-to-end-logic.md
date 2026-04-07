# Certifications — End-to-End Logic

**Module:** Skills
**Feature:** Certifications

---

## Add Certification

### Flow

```
POST /api/v1/skills/certifications
  -> CertificationController.Add(AddCertificationCommand)
    -> [RequirePermission("skills:write")]
    -> CertificationService.AddAsync(command, ct)
      -> 1. Validate: certification_name, issue_date required
      -> 2. If certificate file provided: upload via IFileService
      -> 3. INSERT into employee_certifications
         -> status = 'active'
         -> renewal_reminder_sent = false
      -> Return Result.Success(certDto)
```

## Expiry Tracking

### Flow

```
CertificationExpiryJob (Hangfire, daily)
  -> CertificationService.CheckExpiriesAsync(ct)
    -> 1. Find certifications WHERE expiry_date <= today + 30 days
       AND renewal_reminder_sent = false
    -> 2. For each: send renewal reminder notification
       -> UPDATE renewal_reminder_sent = true
    -> 3. Find certifications WHERE expiry_date < today AND status = 'active'
       -> UPDATE status = 'expired'
```

## Related

- [[certifications]] — feature overview
- [[courses-learning]] — course completion that triggers certification issuance
- [[employee-skills]] — skill validation linked to certification status
- [[event-catalog]] — CertificationExpiringSoon, CertificationExpired events
- [[error-handling]] — Hangfire job retry and failure patterns
