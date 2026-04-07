# Report Definitions — End-to-End Logic

**Module:** Reporting Engine
**Feature:** Report Definitions

---

## Create Report Definition

### Flow

```
POST /api/v1/reports/definitions
  -> ReportDefinitionController.Create(CreateDefinitionCommand)
    -> [RequirePermission("reports:create")]
    -> ReportDefinitionService.CreateAsync(command, ct)
      -> 1. Validate report_type: headcount, turnover, leave_utilization,
         productivity_daily, productivity_weekly, workforce_summary, exception_summary
      -> 2. Validate parameters_json (date range, filters)
      -> 3. If schedule_cron provided:
         -> Validate cron expression
         -> Register Hangfire recurring job
      -> 4. INSERT into report_definitions
      -> Return Result.Success(definitionDto)
```

### Key Rules

- **Scheduled reports** run via Hangfire cron jobs and email results to recipients.
- **On-demand reports** execute immediately and return download link.

## Related

- [[reporting-engine/report-definitions/overview|Report Definitions Overview]]
- [[reporting-engine/report-execution/overview|Report Execution]]
- [[reporting-engine/report-templates/overview|Report Templates]]
- [[event-catalog]]
- [[error-handling]]
