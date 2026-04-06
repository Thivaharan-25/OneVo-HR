# Page: Payroll Management

**Route:** `/hr/payroll` (runs), `/hr/payroll/[id]` (run detail)
**Permission:** `payroll:read` (view), `payroll:run` (execute), `payroll:approve` (approve)

## Purpose

Process payroll runs, review calculations, and approve for payment. Reads actual worked hours from Workforce Presence.

## Payroll Runs Layout

```
┌─────────────────────────────────────────────────────────────┐
│ PageHeader: "Payroll"                       [+ New Run]     │
├─────────────────────────────────────────────────────────────┤
│ ┌───────────┬────────────┬──────────┬──────────┬──────────┐ │
│ │ Run       │ Period     │ Employees│ Total    │ Status   │ │
│ ├───────────┼────────────┼──────────┼──────────┼──────────┤ │
│ │ Mar 2026  │ Mar 1-31   │ 487      │ $1.2M    │ ⏳ Draft  │ │
│ │ Feb 2026  │ Feb 1-28   │ 485      │ $1.18M   │ ✅ Paid   │ │
│ │ Jan 2026  │ Jan 1-31   │ 482      │ $1.15M   │ ✅ Paid   │ │
│ └───────────┴────────────┴──────────┴──────────┴──────────┘ │
│ Pagination                                                  │
└─────────────────────────────────────────────────────────────┘
```

## Run Detail Layout

```
┌─────────────────────────────────────────────────────────────┐
│ ← Back  "March 2026 Payroll"              [Approve] [Lock] │
│ Status: Draft → Calculated → Reviewed → Approved → Paid    │
│         ███████████████░░░░░░░░░░░░░░░░░░░░░░░░░            │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│ Employees│ Gross    │ Deductions│ Net     │ Status         │
│ 487      │ $1.45M   │ $250K     │ $1.2M  │ Draft          │
├──────────┴──────────┴──────────┴──────────┴────────────────┤
│ [Search Employee] [Department ▼] [Variance ▼]              │
├─────────────────────────────────────────────────────────────┤
│ Payslip Table                                              │
│ ┌──────┬──────┬────────┬──────────┬────────┬─────────────┐ │
│ │ Name │ Dept │ Gross  │ Deductions│ Net   │ Variance    │ │
│ ├──────┼──────┼────────┼──────────┼────────┼─────────────┤ │
│ │ J.D. │ Eng  │ $8,500 │ $2,125   │ $6,375│ +$200 ⚠️    │ │
│ │ M.K. │ Sales│ $6,200 │ $1,550   │ $4,650│ $0          │ │
│ └──────┴──────┴────────┴──────────┴────────┴─────────────┘ │
│ Pagination                                                  │
└─────────────────────────────────────────────────────────────┘
```

**Variance column** highlights differences from previous month. Clicking shows breakdown (overtime, bonus, deduction changes).

## Data Sources

| Component | API |
|:----------|:----|
| Run list | `GET /payroll/runs` |
| Run detail | `GET /payroll/runs/{id}` |
| Payslips | `GET /payroll/runs/{id}/payslips?search=&department=` |
| Calculate | `POST /payroll/runs/{id}/calculate` |
| Approve | `PUT /payroll/runs/{id}/approve` |
| Worked hours | Fetched by backend from WorkforcePresence (not directly by frontend) |

## Workflow

1. **Create run** → Draft status, select period
2. **Calculate** → Backend pulls worked hours from WorkforcePresence, applies salary structures, deductions, tax
3. **Review** → HR reviews payslips, checks variances
4. **Approve** → Requires `payroll:approve` permission, locks the run
5. **Pay** → Marks as paid (actual payment via external integration)

## Interactions

- Click run → detail with all payslips
- Click payslip → employee payslip detail (breakdown of all components)
- Variance filter: show only employees with significant changes
- Export: CSV/Excel of the full run

## Empty States

- **No runs:** "No payroll runs yet. Create your first payroll run."
- **Run not calculated:** "Click 'Calculate' to process payroll for this period."
