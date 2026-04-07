# Payroll Audit Trail — End-to-End Logic

**Module:** Payroll
**Feature:** Audit Trail

---

## Record Audit Entry

### Flow

```
Every payroll action automatically creates an audit entry:
  -> PayrollAuditService.LogAsync(payrollRunId, action, details, ct)
    -> INSERT into payroll_audit_trail
    -> Actions tracked: run_started, run_completed, run_failed,
       payslip_generated, adjustment_added, run_approved
```

## Query Audit Trail

### Flow

```
GET /api/v1/payroll/runs/{id}/audit
  -> PayrollAuditController.GetAudit(runId)
    -> [RequirePermission("payroll:read")]
    -> PayrollAuditService.GetAuditAsync(runId, ct)
      -> Query payroll_audit_trail WHERE payroll_run_id ORDER BY created_at
      -> Return Result.Success(auditEntries)

```

## Related

- [[payroll/audit-trail/overview|Audit Trail Overview]]
- [[payroll/payroll-execution/overview|Payroll Execution]]
- [[payroll/adjustments/overview|Adjustments]]
- [[error-handling]]
- [[shared-kernel]]
- [[WEEK4-payroll]]
