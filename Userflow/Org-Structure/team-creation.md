# Team Creation

**Area:** Org Structure  
**Required Permission(s):** `org:manage`  
**Related Permissions:** `employees:read` (to assign members)

---

## Preconditions

- Department exists → [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Teams
- **UI:** Sidebar → Organization → Teams → click "Create Team"
- **API:** `GET /api/v1/org/teams`

### Step 2: Define Team
- **UI:** Enter team name → select parent department → add description
- **Validation:** Name unique within department

### Step 3: Assign Team Lead
- **UI:** Search and select employee as team lead
- **Backend:** Team lead gains `*:read-team` scope for this team's members

### Step 4: Add Members
- **UI:** Search employees → add to team → employees can belong to multiple teams
- **API:** `POST /api/v1/org/teams`
- **DB:** `teams`, `team_members` — records created

### Step 5: Confirmation
- **UI:** Team visible in department view → team lead can see team dashboard

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate name in department | Validation fails | "Team name already exists in this department" |
| Team lead not in department | Warning | "Team lead is not a member of the parent department" |

## Events Triggered

- `TeamCreated` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]]

## Module References

- [[modules/org-structure/teams/overview|Teams]]
- [[modules/org-structure/overview|Org Structure]]
