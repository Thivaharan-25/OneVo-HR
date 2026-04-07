# Leave Type Configuration

**Area:** Leave Management  
**Required Permission(s):** `leave:manage`  
**Related Permissions:** `settings:admin` (for global defaults)

---

## Preconditions

- Tenant has been provisioned and is active
- User has `leave:manage` permission assigned via their Job Family role
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Leave Type Configuration
- **UI:** User navigates to Leave → Configuration → Leave Types. Sees a list of existing leave types (system defaults like Annual, Sick are pre-seeded)
- **API:** `GET /api/v1/leave/types`
- **Backend:** `LeaveTypeService.GetAllAsync()` → [[leave]]
- **Validation:** Checks `leave:manage` permission via RBAC middleware
- **DB:** `leave_types` (filtered by `tenant_id`)

### Step 2: Create New Leave Type
- **UI:** Click "Create Leave Type" button → modal/page opens with form fields: Name, Code (auto-generated, editable), Description, Category dropdown (Annual, Sick, Maternity, Paternity, Compassionate, Unpaid, Custom)
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** Client-side: Name is required, Code must be unique
- **DB:** None

### Step 3: Configure Entitlement Rules
- **UI:** Section: "Entitlement Rules" — fields: Default Days Per Year (numeric), Carry-Forward Allowed (toggle), Max Carry-Forward Days (numeric, shown if toggle on), Carry-Forward Expiry (months after year-end), Pro-rata for New Joiners (toggle)
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** Max Carry-Forward Days cannot exceed Default Days Per Year. Expiry must be 1–12 months
- **DB:** None

### Step 4: Configure Approval and Pay Rules
- **UI:** Section: "Approval & Pay" — fields: Requires Approval (toggle, default: on), Paid Leave (toggle), Applicable Gender (All / Male / Female — shown for maternity/paternity types), Minimum Notice Period (days, 0 = no notice required), Max Consecutive Days Allowed (numeric, 0 = unlimited)
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** If category is Maternity, Applicable Gender auto-set to Female. If Paternity, auto-set to Male
- **DB:** None

### Step 5: Configure Supporting Document Rules
- **UI:** Section: "Documentation" — fields: Requires Supporting Document (toggle), Document Required After N Days (numeric, e.g., medical certificate after 3 sick days), Accepted Document Types (checkboxes: PDF, Image)
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** Document threshold must be ≥ 1 if enabled
- **DB:** None

### Step 6: Save Leave Type
- **UI:** Click "Save" button. Success toast shown. Redirected back to leave types list
- **API:** `POST /api/v1/leave/types`
- **Backend:** `LeaveTypeService.CreateAsync()` → [[leave]]
  1. Validates uniqueness of code within tenant
  2. Creates `leave_types` record with all configuration
  3. Publishes `LeaveTypeCreatedEvent`
  4. Creates audit log entry
- **Validation:** Code unique per tenant. Name unique per tenant. Days must be positive integers
- **DB:** `leave_types`, `audit_logs`

## Variations

### When editing an existing leave type
- Navigate to Leave Types → click existing type → Edit
- All fields editable except Code (immutable after creation)
- Changes apply to future entitlements only; existing entitlements unchanged
- API: `PUT /api/v1/leave/types/{leaveTypeId}`

### When deactivating a leave type
- Toggle "Active" to off → confirmation dialog: "Employees with existing balances will retain them but cannot submit new requests"
- API: `PATCH /api/v1/leave/types/{leaveTypeId}/status`
- Existing approved leaves remain valid; pending requests auto-cancelled

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate leave type code | `409 Conflict` returned | "A leave type with this code already exists" |
| Duplicate leave type name | `409 Conflict` returned | "A leave type with this name already exists" |
| Invalid carry-forward config | Validation fails | "Carry-forward days cannot exceed default annual entitlement" |
| Deactivate type with pending requests | Warning shown | "There are N pending requests for this leave type. They will be auto-cancelled. Continue?" |
| Missing required permission | `403 Forbidden` | "You do not have permission to manage leave types" |

## Events Triggered

- `LeaveTypeCreatedEvent` → [[event-catalog]] — consumed by leave policy engine to make type available for policy assignment
- `LeaveTypeUpdatedEvent` → [[event-catalog]] — consumed by entitlement recalculation service
- `AuditLogEntry` (action: `leave_type.created`) → [[audit-logging]]

## Related Flows

- [[leave-policy-setup]] — create policies that reference these leave types
- [[leave-entitlement-assignment]] — assign entitlements based on configured types
- [[leave-request-submission]] — employees request leave using these types

## Module References

- [[leave]] — leave module overview and architecture
- [[leave-types]] — leave type data model and business rules
- [[configuration]] — system-wide configuration patterns
