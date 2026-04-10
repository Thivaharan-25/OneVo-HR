# Certification Tracking

**Area:** Skills & Learning  
**Trigger:** Employee uploads certification (user action — self-service)
**Required Permission(s):** `skills:write` (own) or `skills:manage` (admin)  
**Related Permissions:** `documents:write` (upload certificate)

---

## Preconditions

- Employee profile exists → [[Userflow/Employee-Management/profile-management|Profile Management]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Add Certification
- **UI:** Profile → Skills → Certifications → "Add Certification" → enter: cert name, issuing body (e.g., AWS, Microsoft), date obtained, expiry date (if applicable) → upload certificate document
- **API:** `POST /api/v1/skills/certifications`
- **Backend:** CertificationService.AddAsync() → [[modules/skills/certifications/overview|Certifications]]
- **DB:** `employee_certifications` — record with optional `document_id`

### Step 2: Expiry Tracking
- **Backend:** System monitors expiry dates → sends reminder notification 30/60/90 days before expiry
- Notification → [[backend/notification-system|Notification System]]

### Step 3: Renewal
- **UI:** Expired cert shows "Expired" badge → employee uploads renewed cert → updates expiry date

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Expiry before obtained date | Validation fails | "Expiry must be after date obtained" |
| File too large | Upload fails | "Max file size is 10MB" |

## Events Triggered

- `CertificationAdded` → [[backend/messaging/event-catalog|Event Catalog]]
- `CertificationExpiring` → [[backend/messaging/event-catalog|Event Catalog]] (automated)

## Related Flows

- [[Userflow/Skills-Learning/employee-skill-declaration|Employee Skill Declaration]]
- [[Userflow/Employee-Management/qualification-tracking|Qualification Tracking]]
- [[Userflow/Documents/document-upload|Document Upload]]

## Module References

- [[modules/skills/certifications/overview|Certifications]]
- [[modules/documents/document-management/overview|Document Management]]
