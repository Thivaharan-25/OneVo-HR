# Qualification Tracking

**Area:** Employee Management  
**Required Permission(s):** `employees:read-own` (own) or `employees:write` (admin)  
**Related Permissions:** `documents:write` (upload supporting docs)

---

## Preconditions

- Employee exists and is active
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Qualifications
- **UI:** Employee Profile → Qualifications tab
- **API:** `GET /api/v1/employees/{id}/qualifications`

### Step 2: Add Qualification
- **UI:** Click "Add" → select type:
  - **Education:** Degree, institution, field of study, start/end year, GPA
  - **Certification:** Cert name, issuing body, date obtained, expiry date
  - **Work Experience:** Company, title, start/end dates, description
- **Validation:** End date after start date, required fields per type

### Step 3: Upload Supporting Document
- **UI:** Attach certificate/diploma image or PDF → uploaded to file storage
- **API:** `POST /api/v1/employees/{id}/qualifications`
- **Backend:** QualificationService.AddAsync() → [[qualifications]]
- **DB:** `employee_qualifications` — record with optional `document_id` FK

### Step 4: Verification (if admin)
- **UI:** Admin can mark qualification as "Verified" after checking documents
- **DB:** `verified_at`, `verified_by` fields updated

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Invalid date range | Validation fails | "End date must be after start date" |
| File too large | Upload fails | "Maximum file size is 10MB" |

## Events Triggered

- `QualificationAdded` → [[event-catalog]]

## Related Flows

- [[profile-management]]
- [[certification-tracking]]
- [[document-upload]]

## Module References

- [[qualifications]]
- [[document-management]]
