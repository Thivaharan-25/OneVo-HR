# Qualifications — End-to-End Logic

**Module:** Core HR
**Feature:** Qualifications & Work History

---

## Add Qualification

### Flow

```
POST /api/v1/employees/{id}/qualifications
  -> QualificationController.Add(id, AddQualificationCommand)
    -> [RequirePermission("employees:write")] or own profile
    -> QualificationService.AddAsync(employeeId, command, ct)
      -> 1. Validate qualification_type: degree, certification, license
      -> 2. If document provided:
         -> Upload via IFileService.UploadFileAsync()
         -> Store document_file_id
      -> 3. INSERT into employee_qualifications
      -> Return Result.Success(qualificationDto)
```

## Add Work History

### Flow

```
POST /api/v1/employees/{id}/work-history
  -> WorkHistoryController.Add(id, AddWorkHistoryCommand)
    -> [RequirePermission("employees:write")] or own profile
    -> WorkHistoryService.AddAsync(employeeId, command, ct)
      -> 1. Validate: company_name, job_title, start_date required
      -> 2. INSERT into employee_work_history
      -> Return Result.Success(workHistoryDto)
```

### Key Rules

- **Qualification documents stored in blob storage** via `IFileService`, only metadata in DB.
- **Expiry tracking:** `expiry_date` on qualifications can trigger renewal reminders.

## Related

- [[modules/core-hr/qualifications/overview|Qualifications Overview]]
- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/core-hr/onboarding/overview|Onboarding]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
