# Document Acknowledgement

**Area:** Documents  
**Required Permission(s):** Any employee (for assigned documents)  
**Related Permissions:** `documents:manage` (track acknowledgement status)

---

## Preconditions

- Policy document uploaded with acknowledgement required → [[Userflow/Documents/document-upload|Document Upload]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Receive Notification
- **UI:** Notification: "New policy requires your acknowledgement: [Document Title]"
- **API:** `GET /api/v1/documents/acknowledgements/pending`

### Step 2: Read Document
- **UI:** Click notification → document opens → must scroll through / spend minimum time before acknowledge button activates

### Step 3: Acknowledge
- **UI:** Click "I have read and understood this document" → checkbox confirmation → submit
- **API:** `POST /api/v1/documents/{id}/acknowledge`
- **Backend:** AcknowledgementService.AcknowledgeAsync() → [[modules/documents/acknowledgements/overview|Acknowledgements]]
- **DB:** `document_acknowledgements` — employee_id, timestamp, IP address

### Step 4: Admin Tracking
- **UI:** Admin views Documents → Acknowledgements → see completion rate per document → list of pending employees → send reminder to overdue employees

## Variations

### Overdue acknowledgements
- System sends automatic reminders at configured intervals → escalates to manager if still pending

### Updated document
- When new version uploaded → all previous acknowledgements reset → employees re-notified

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Already acknowledged | No action needed | "You have already acknowledged this document" |
| Document withdrawn | Removed from pending | Acknowledgement request disappears |

## Events Triggered

- `DocumentAcknowledged` → [[backend/messaging/event-catalog|Event Catalog]]
- `AcknowledgementOverdue` → [[backend/messaging/event-catalog|Event Catalog]] (automated)

## Related Flows

- [[Userflow/Documents/document-upload|Document Upload]]
- [[Userflow/Documents/document-versioning|Document Versioning]]
- [[Userflow/Notifications/notification-preference-setup|Notification Preference Setup]]

## Module References

- [[modules/documents/acknowledgements/overview|Acknowledgements]]
- [[modules/documents/document-management/overview|Document Management]]
- [[backend/notification-system|Notification System]]
