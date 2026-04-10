# Payslip View

**Area:** Payroll  
**Trigger:** Employee navigates to payslip page after payroll run (user action — view only)
**Required Permission(s):** `payroll:read` (own payslips)  
**Related Permissions:** `payroll:write` (view all employee payslips)

---

## Preconditions

- At least one approved payroll run including the employee → [[Userflow/Payroll/payroll-run-execution|Payroll Run Execution]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Payslips
- **UI:** Dashboard → "My Payslips" or Sidebar → Payroll → My Payslips
- **API:** `GET /api/v1/payroll/payslips/me`

### Step 2: Select Month
- **UI:** List of available payslips by month/year → click to view
- **API:** `GET /api/v1/payroll/payslips/{id}`

### Step 3: View Breakdown
- **UI:** Detailed view showing:
  - **Earnings:** Base salary, each allowance line, overtime pay, bonuses
  - **Deductions:** Income tax, pension, social security, other deductions
  - **Net Pay:** Final amount
  - **Employer Contributions:** (optional, if enabled) pension + social security (employer portion)
  - **Year-to-Date:** Cumulative totals

### Step 4: Download
- **UI:** Click "Download PDF" → formatted payslip with company logo
- **API:** `GET /api/v1/payroll/payslips/{id}/download`

## Variations

### Admin viewing employee payslips
- With `payroll:write`: can navigate to any employee's payslip history

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No payslips available | Empty state | "No payslips available yet" |
| PDF generation fails | Retry | "Payslip download failed — try again" |

## Events Triggered

- None (read-only flow)

## Related Flows

- [[Userflow/Payroll/payroll-run-execution|Payroll Run Execution]]
- [[Userflow/Employee-Management/compensation-setup|Compensation Setup]]

## Module References

- [[modules/payroll/payroll-execution/overview|Payroll Execution]]
- [[modules/documents/overview|Documents]]
