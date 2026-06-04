# Certification Tracking

**Area:** Skills & Learning  

**Phase:** Phase 2 deferred
**Trigger:** Employee uploads certification (user action â€” self-service)
**Required Permission(s):** `skills:write` (own) or `skills:manage` (admin)  
**Related Permissions:** `documents:write` (upload certificate)

---

## Preconditions

- Employee profile exists â†’ [[Userflow/Employee-Management/profile-management|Profile Management]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

The steps below are Phase 2 only. Do not build Skills certification pages or /api/v1/skills/certifications integrations in Phase 1.

### Step 1: Add Certification
- **UI:** Profile â†’ Skills â†’ Certifications â†’ "Add Certification" â†’ enter: cert name, issuing body (e.g., AWS, Microsoft), date obtained, expiry date (if applicable) â†’ upload certificate document
- **API:** `POST /api/v1/skills/certifications`
- **Backend:** CertificationService.AddAsync() â†’ [[modules/skills/certifications/overview|Certifications]]
- **DB:** `employee_certifications` â€” record with optional `document_id`

### Step 2: Expiry Tracking
- **Backend:** System monitors expiry dates â†’ sends reminder notification 30/60/90 days before expiry
- Notification â†’ [[backend/notification-system|Notification System]]

### Step 3: Renewal
- **UI:** Expired cert shows "Expired" badge â†’ employee uploads renewed cert â†’ updates expiry date

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Expiry before obtained date | Validation fails | "Expiry must be after date obtained" |
| File too large | Upload fails | "Max file size is 10MB" |

## Events Triggered

- `CertificationAdded` â†’ [[backend/messaging/event-catalog|Event Catalog]]
- `CertificationExpiring` â†’ [[backend/messaging/event-catalog|Event Catalog]] (automated)

## Related Flows

- [[Userflow/Skills-Learning/employee-skill-declaration|Employee Skill Declaration]]
- [[Userflow/Employee-Management/qualification-tracking|Qualification Tracking]]
- [[Userflow/Documents/document-upload|Document Upload]]

## Module References

- [[modules/skills/certifications/overview|Certifications]]
- [[modules/documents/document-management/overview|Document Management]]

