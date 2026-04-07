# Recognition Submission

**Area:** Performance  
**Required Permission(s):** `performance:write` (any authenticated employee)  
**Related Permissions:** `performance:manage` (view all recognitions)

---

## Preconditions

- Sender and recipient are active employees
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Give Recognition
- **UI:** Performance → Recognition → "Give Recognition" → search and select colleague → select category (Teamwork, Innovation, Leadership, Customer Focus, Going Above & Beyond)
- **API:** `POST /api/v1/performance/recognitions`

### Step 2: Write Message
- **UI:** Write appreciation message → optionally add badge/award → submit
- **Backend:** RecognitionService.SubmitAsync() → [[recognitions]]
- **DB:** `recognitions` — record created

### Step 3: Recipient Notified
- **UI:** Recipient sees notification + recognition appears on company feed/wall
- **Backend:** Notification sent → [[notification-system]]

### Step 4: Recognition Feed
- **UI:** Company-wide recognition feed visible on dashboard → filter by department → most recognized employees shown

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Self-recognition | Blocked | "Cannot recognize yourself" |
| Inactive recipient | Blocked | "Employee is no longer active" |

## Events Triggered

- `RecognitionSubmitted` → [[event-catalog]]
- Notification to recipient → [[notification-system]]

## Related Flows

- [[review-cycle-setup]]
- [[profile-management]]

## Module References

- [[recognitions]]
