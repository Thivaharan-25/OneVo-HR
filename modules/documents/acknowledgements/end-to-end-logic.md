# Document Acknowledgements — End-to-End Logic

**Module:** Documents
**Feature:** Acknowledgements

---

## Acknowledge Document

### Flow

```
POST /api/v1/documents/{id}/acknowledge
  -> AcknowledgementController.Acknowledge(id, AcknowledgeCommand)
    -> [Authenticated]
    -> AcknowledgementService.AcknowledgeAsync(documentVersionId, ct)
      -> 1. Validate document requires_acknowledgement = true
      -> 2. Check not already acknowledged by this employee
      -> 3. INSERT into document_acknowledgements
         -> method = 'click' or 'e_signature'
         -> ip_address from HttpContext
      -> 4. Notify document owner of acknowledgement
      -> Return Result.Success()
```

## Get Pending Acknowledgements

### Flow

```
GET /api/v1/documents/pending-acknowledgements
  -> AcknowledgementController.GetPending()
    -> [Authenticated]
    -> AcknowledgementService.GetPendingAsync(employeeId, ct)
      -> 1. Find all documents with requires_acknowledgement = true
      -> 2. LEFT JOIN document_acknowledgements
      -> 3. Return documents where acknowledgement is missing
      -> Return Result.Success(pendingDocs)
```

## Related

- [[frontend/architecture/overview|Acknowledgements Overview]]
- [[frontend/architecture/overview|Document Management]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
