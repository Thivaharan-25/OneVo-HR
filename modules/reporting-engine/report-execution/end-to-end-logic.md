# Report Execution — End-to-End Logic

**Module:** Reporting Engine
**Feature:** Report Execution

---

## Execute Report

### Flow

```
POST /api/v1/reports/execute/{definitionId}
  -> ReportExecutionController.Execute(definitionId)
    -> [RequirePermission("reports:create")]
    -> ReportExecutionService.ExecuteAsync(definitionId, ct)
      -> 1. Load report definition
      -> 2. INSERT into report_executions (status = 'running')
      -> 3. Based on report_type, fetch data:
         -> headcount: IEmployeeService.GetAllAsync()
         -> leave_utilization: ILeaveService data
         -> productivity_daily: IProductivityAnalyticsService.GetDailyReportAsync()
         -> workforce_summary: IProductivityAnalyticsService.GetWorkforceSnapshotAsync()
      -> 4. Apply template columns/filters from report_templates
      -> 5. Generate output file (CSV or XLSX via ClosedXML)
      -> 6. Upload file via IFileService
      -> 7. UPDATE report_executions: status = 'completed', file_record_id
      -> 8. If recipients configured: email report via notifications
      -> Return Result.Success(executionDto with download link)
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Definition not found | Return 404 |
| Data source unavailable | Status = 'failed', error_message logged |
| File generation failure | Status = 'failed', retry once |

## Related

- [[frontend/architecture/overview|Report Execution Overview]]
- [[frontend/architecture/overview|Report Definitions]]
- [[frontend/architecture/overview|Report Templates]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
