# Certification Tracking

**Area:** Skills & Learning  
**Required Permission(s):** `skills:write` (own) or `skills:manage` (admin)  
**Related Permissions:** `documents:write` (upload certificate)

---

## Preconditions

- Employee profile exists → [[profile-management]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Add Certification
- **UI:** Profile → Skills → Certifications → "Add Certification" → enter: cert name, issuing body (e.g., AWS, Microsoft), date obtained, expiry date (if applicable) → upload certificate document
- **API:** `POST /api/v1/skills/certifications`
- **Backend:** CertificationService.AddAsync() → [[certifications]]
- **DB:** `employee_certifications` — record with optional `document_id`

### Step 2: Expiry Tracking
- **Backend:** System monitors expiry dates → sends reminder notification 30/60/90 days before expiry
- Notification → [[notification-system]]

### Step 3: Renewal
- **UI:** Expired cert shows "Expired" badge → employee uploads renewed cert → updates expiry date

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Expiry before obtained date | Validation fails | "Expiry must be after date obtained" |
| File too large | Upload fails | "Max file size is 10MB" |

## Events Triggered

- `CertificationAdded` → [[event-catalog]]
- `CertificationExpiring` → [[event-catalog]] (automated)

## Related Flows

- [[employee-skill-declaration]]
- [[qualification-tracking]]
- [[document-upload]]

## Module References

- [[certifications]]
- [[document-management]]
