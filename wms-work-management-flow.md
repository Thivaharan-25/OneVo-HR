# WMS Work Management — User Flow & Entity Map

> Modules filtered for work management. Each module lists its features, entities, attributes, and relationships.

---

## User Flow

`AUTH` → `ORG` → `PROJECT` → `PLANNING` → `TASK` → `COLLAB` → `CHAT` → `TIME` → `RESOURCE` → `NOTIFY` → `REMINDER` → `INSIGHT` → `INTEGRATION`

---

## Modules

### 1. Authentication (`auth`)
**Features:** Login · Session · Security · Recovery

**Entities & Attributes:**

| Entity | Attributes |
|---|---|
| `AUTH_ACCOUNT` | id (PK, uuid), email (string), password_hash (string), is_verified (boolean), created_at (timestamp) |
| `AUTH_SESSION` | id (PK, uuid), user_id (FK, uuid), workspace_id (FK, uuid), token_hash (string), expires_at (timestamp) |
| `AUTH_DEVICE` | id (PK, uuid), user_id (FK, uuid), name (string), device_type (enum), last_seen_at (timestamp) |
| `AUTH_PROVIDER` | id (PK, uuid), user_id (FK, uuid), provider (enum), provider_user_id (string), is_active (boolean) |
| `MFA_CONFIG` | id (PK, uuid), user_id (FK, uuid), method (enum), is_enabled (boolean), verified_at (timestamp) |
| `AUDIT_LOG` | id (PK, uuid), user_id (FK, uuid), workspace_id (FK, uuid), event_type (enum), created_at (timestamp) |
| `PASSWORD_RESET_TOKEN` | id (PK, uuid), user_id (FK, uuid), token_hash (string), expires_at (timestamp), used_at (timestamp) |
| `ACCESS_POLICY` | id (PK, uuid), workspace_id (FK, uuid), policy_type (enum), config (json), is_active (boolean) |

---

### 2. Organization — Workspace & Users (`org`)
**Features:** Workspace setup · Teams · Roles · Departments

**Entities & Attributes:**

| Entity | Attributes |
|---|---|
| `WORKSPACE` | id (PK, uuid), name (string), slug (string), owner_id (FK, uuid), created_at (timestamp) |
| `USER` | id (PK, uuid), workspace_id (FK, uuid), role_id (FK, uuid), name (string), email (string) |
| `ROLE` | id (PK, uuid), workspace_id (FK, uuid), name (string), permissions (json), created_at (timestamp) |
| `TEAM` | id (PK, uuid), workspace_id (FK, uuid), name (string), description (text), created_at (timestamp) |
| `TEAM_MEMBER` | id (PK, uuid), team_id (FK, uuid), user_id (FK, uuid), role (enum), joined_at (timestamp) |
| `INVITE` | id (PK, uuid), workspace_id (FK, uuid), email (string), role_id (FK, uuid), expires_at (timestamp) |
| `USER_PREFERENCE` | id (PK, uuid), user_id (FK, uuid), theme (enum), language (string), timezone (string) |
| `WORKSPACE_BILLING` | id (PK, uuid), workspace_id (FK, uuid), plan (enum), billing_cycle (enum), is_active (boolean) |
| `DEPARTMENT` | id (PK, uuid), workspace_id (FK, uuid), name (string), lead_user_id (FK, uuid), created_at (timestamp) |

---

### 3. Project Management (`project`)
**Features:** Project setup · Membership · Milestones · Change control

**Entities & Attributes:**

| Entity | Attributes |
|---|---|
| `PROJECT` | id (PK, uuid), workspace_id (FK, uuid), name (string), status (enum), created_at (timestamp) |
| `PROJECT_MEMBER` | id (PK, uuid), project_id (FK, uuid), user_id (FK, uuid), role (enum), joined_at (timestamp) |
| `PROJECT_COMPONENT` | id (PK, uuid), project_id (FK, uuid), name (string), lead_id (FK, uuid), created_at (timestamp) |
| `EPIC` | id (PK, uuid), project_id (FK, uuid), title (string), status (enum), end_date (date) |
| `MILESTONE` | id (PK, uuid), project_id (FK, uuid), name (string), target_date (date), status (enum) |
| `PROJECT_SETTING` | id (PK, uuid), project_id (FK, uuid), timezone (string), default_priority (enum), working_days (json) |
| `CHANGE_REQUEST` | id (PK, uuid), project_id (FK, uuid), requested_by (FK, uuid), title (string), status (enum) |

---

### 4. Task Management — Issues & Bugs (`task`)
**Features:** Issue tracking · Bug lifecycle · Labeling · Submission · Approval

**Entities & Attributes:**

| Entity | Attributes |
|---|---|
| `TASK` | id (PK, uuid), project_id (FK, uuid), title (string), priority (enum), status (enum) |
| `ISSUE_TYPE` | id (PK, uuid), workspace_id (FK, uuid), name (string), color (string), is_default (boolean) |
| `TASK_ASSIGNEE` | id (PK, uuid), task_id (FK, uuid), user_id (FK, uuid), assigned_by (FK, uuid), assigned_at (timestamp) |
| `CHECKLIST_ITEM` | id (PK, uuid), task_id (FK, uuid), title (string), is_checked (boolean), position (int) |
| `TASK_DEPENDENCY` | id (PK, uuid), task_id (FK, uuid), depends_on_id (FK, uuid), type (enum), created_at (timestamp) |
| `LABEL` | id (PK, uuid), project_id (FK, uuid), name (string), color (string), created_at (timestamp) |
| `TASK_LABEL` | task_id (FK, uuid), label_id (FK, uuid), linked_at (timestamp) |
| `TASK_SUBMISSION` | id (PK, uuid), task_id (FK, uuid), submitted_by (FK, uuid), notes (text), status (enum) |
| `TASK_SUBMISSION_FILE` | id (PK, uuid), submission_id (FK, uuid), file_asset_id (FK, uuid), uploaded_at (timestamp), is_primary (boolean) |
| `TASK_APPROVAL` | id (PK, uuid), task_id (FK, uuid), requested_by (FK, uuid), approver_id (FK, uuid), status (enum) |
| `TASK_REOPEN_LOG` | id (PK, uuid), task_id (FK, uuid), reopened_by (FK, uuid), reason (text), reopened_at (timestamp) |
| `BUG_REPORT` | id (PK, uuid), project_id (FK, uuid), title (string), severity (enum), status (enum) |
| `BUG_REPRODUCTION_STEP` | id (PK, uuid), bug_id (FK, uuid), step_number (int), action (text), expected (text) |
| `BUG_RESOLUTION` | id (PK, uuid), bug_id (FK, uuid), resolution_type (enum), resolved_by (FK, uuid), resolved_at (timestamp) |

---

### 5. Planning (`planning`)
**Features:** Sprint plan · Boards · Roadmap · Release

**Entities & Attributes:**

| Entity | Attributes |
|---|---|
| `SPRINT` | id (PK, uuid), project_id (FK, uuid), name (string), start_date (date), end_date (date) |
| `SPRINT_REPORT` | id (PK, uuid), sprint_id (FK, uuid), velocity (float), completed_points (int), created_at (timestamp) |
| `BOARD` | id (PK, uuid), project_id (FK, uuid), name (string), type (enum), is_default (boolean) |
| `BOARD_VIEW` | id (PK, uuid), board_id (FK, uuid), user_id (FK, uuid), view_type (enum), is_default (boolean) |
| `ROADMAP` | id (PK, uuid), workspace_id (FK, uuid), name (string), start_date (date), end_date (date) |
| `ROADMAP_ITEM` | id (PK, uuid), roadmap_id (FK, uuid), entity_type (enum), entity_id (uuid), position (int) |
| `BASELINE` | id (PK, uuid), project_id (FK, uuid), snapshot (json), created_at (timestamp) |
| `VERSION` | id (PK, uuid), project_id (FK, uuid), name (string), status (enum), release_date (date) |
| `RELEASE_CALENDAR` | id (PK, uuid), project_id (FK, uuid), version_id (FK, uuid), release_at (timestamp), status (enum) |

---

### 6. Goal & OKR (`okr`)
**Features:** Objectives · Key results · Progress updates · Check-ins

**Entities & Attributes:**

| Entity | Attributes |
|---|---|
| `OBJECTIVE` | id (PK, uuid), workspace_id (FK, uuid), owner_id (FK, uuid), title (string), progress (float) |
| `KEY_RESULT` | id (PK, uuid), objective_id (FK, uuid), title (string), target_value (float), status (enum) |
| `OKR_UPDATE` | id (PK, uuid), entity_type (enum), entity_id (uuid), new_value (float), created_at (timestamp) |
| `OKR_ALIGNMENT` | id (PK, uuid), parent_objective_id (FK, uuid), child_objective_id (FK, uuid), contribution_weight (float), created_at (timestamp) |
| `INITIATIVE` | id (PK, uuid), key_result_id (FK, uuid), title (string), status (enum), created_at (timestamp) |
| `GOAL_CHECKIN` | id (PK, uuid), objective_id (FK, uuid), author_id (FK, uuid), progress_delta (float), created_at (timestamp) |

---

### 7. Time Management (`time`)
**Features:** Time logging · Timesheets · Reports · Overtime

**Entities & Attributes:**

| Entity | Attributes |
|---|---|
| `TIME_LOG` | id (PK, uuid), task_id (FK, uuid), user_id (FK, uuid), duration_mins (int), logged_at (timestamp) |
| `TIMESHEET` | id (PK, uuid), user_id (FK, uuid), period_start (date), period_end (date), status (enum) |
| `TIMESHEET_ENTRY` | id (PK, uuid), timesheet_id (FK, uuid), task_id (FK, uuid), duration_mins (int), date (date) |
| `BILLABLE_RATE` | id (PK, uuid), workspace_id (FK, uuid), user_id (FK, uuid), rate (float), currency (string) |
| `TIME_REPORT` | id (PK, uuid), workspace_id (FK, uuid), project_id (FK, uuid), report_type (enum), generated_at (timestamp) |
| `TIMER_SESSION` | id (PK, uuid), user_id (FK, uuid), task_id (FK, uuid), started_at (timestamp), duration_mins (int) |
| `OVERTIME_ENTRY` | id (PK, uuid), user_id (FK, uuid), task_id (FK, uuid), minutes (int), approved_at (timestamp) |

---

### 8. Resource Management (`resource`)
**Features:** Skills · Allocation · Capacity · Allocation history

**Entities & Attributes:**

| Entity | Attributes |
|---|---|
| `SKILL` | id (PK, uuid), workspace_id (FK, uuid), name (string), category (string), created_at (timestamp) |
| `USER_SKILL` | id (PK, uuid), user_id (FK, uuid), skill_id (FK, uuid), proficiency_level (enum), verified_at (timestamp) |
| `RESOURCE_PLAN` | id (PK, uuid), project_id (FK, uuid), user_id (FK, uuid), allocation_pct (int), status (enum) |
| `CAPACITY_SNAPSHOT` | id (PK, uuid), workspace_id (FK, uuid), user_id (FK, uuid), week_start (date), utilization_pct (float) |
| `SKILL_REQUIREMENT` | id (PK, uuid), project_id (FK, uuid), skill_id (FK, uuid), required_level (enum), headcount (int) |
| `RESOURCE_ALLOCATION_LOG` | id (PK, uuid), resource_plan_id (FK, uuid), changed_by (FK, uuid), old_pct (int), new_pct (int) |

---

### 9. Chat & Messaging (`chat`)
**Features:** Channels · Messages · DM · Read receipts

**Entities & Attributes:**

| Entity | Attributes |
|---|---|
| `CHANNEL` | id (PK, uuid), workspace_id (FK, uuid), name (string), type (enum), created_at (timestamp) |
| `CHANNEL_MEMBER` | id (PK, uuid), channel_id (FK, uuid), user_id (FK, uuid), role (enum), joined_at (timestamp) |
| `MESSAGE` | id (PK, uuid), channel_id (FK, uuid), sender_id (FK, uuid), body (text), created_at (timestamp) |
| `MESSAGE_REACTION` | id (PK, uuid), message_id (FK, uuid), user_id (FK, uuid), emoji (string), created_at (timestamp) |
| `MESSAGE_ATTACHMENT` | id (PK, uuid), message_id (FK, uuid), uploaded_by (FK, uuid), file_asset_id (FK, uuid), created_at (timestamp) |
| `DIRECT_MESSAGE_CHANNEL` | id (PK, uuid), workspace_id (FK, uuid), is_group (boolean), name (string), created_at (timestamp) |
| `DM_PARTICIPANT` | id (PK, uuid), dm_channel_id (FK, uuid), user_id (FK, uuid), is_muted (boolean), joined_at (timestamp) |
| `MESSAGE_READ_RECEIPT` | id (PK, uuid), message_id (FK, uuid), user_id (FK, uuid), read_at (timestamp), source (enum) |

---

### 10. Collaboration (`collab`)
**Features:** Comments · Attachments · Wiki · File management · Review comments

**Entities & Attributes:**

| Entity | Attributes |
|---|---|
| `COMMENT` | id (PK, uuid), task_id (FK, uuid), author_id (FK, uuid), body (text), created_at (timestamp) |
| `REACTION` | id (PK, uuid), comment_id (FK, uuid), user_id (FK, uuid), emoji (string), created_at (timestamp) |
| `MENTION` | id (PK, uuid), comment_id (FK, uuid), mentioned_user_id (FK, uuid), created_at (timestamp) |
| `ATTACHMENT` | id (PK, uuid), task_id (FK, uuid), uploaded_by (FK, uuid), file_url (string), created_at (timestamp) |
| `FILE_ASSET` | id (PK, uuid), workspace_id (FK, uuid), uploaded_by (FK, uuid), file_name (string), mime_type (string) |
| `FILE_VERSION` | id (PK, uuid), file_asset_id (FK, uuid), version_no (int), storage_url (string), uploaded_at (timestamp) |
| `DOCUMENT` | id (PK, uuid), workspace_id (FK, uuid), project_id (FK, uuid), title (string), status (enum) |
| `DOCUMENT_VERSION` | id (PK, uuid), document_id (FK, uuid), version_no (int), body (text), created_at (timestamp) |
| `DOCUMENT_APPROVAL` | id (PK, uuid), document_id (FK, uuid), requested_by (FK, uuid), approver_id (FK, uuid), status (enum) |
| `WIKI_PAGE` | id (PK, uuid), project_id (FK, uuid), title (string), slug (string), updated_at (timestamp) |
| `WIKI_VERSION` | id (PK, uuid), wiki_page_id (FK, uuid), author_id (FK, uuid), body (text), created_at (timestamp) |
| `ACTIVITY_LOG` | id (PK, uuid), workspace_id (FK, uuid), actor_id (FK, uuid), action (enum), created_at (timestamp) |
| `APPROVAL_COMMENT` | id (PK, uuid), task_approval_id (FK, uuid), author_id (FK, uuid), comment (text), created_at (timestamp) |

---

### 11. Notifications (`notify`)
**Features:** Alerts · Batch · Digest · Rules

**Entities & Attributes:**

| Entity | Attributes |
|---|---|
| `NOTIFICATION` | id (PK, uuid), user_id (FK, uuid), type (enum), title (string), created_at (timestamp) |
| `NOTIFICATION_DELIVERY` | id (PK, uuid), notification_id (FK, uuid), channel (enum), status (enum), attempted_at (timestamp) |
| `NOTIFICATION_BATCH` | id (PK, uuid), user_id (FK, uuid), batch_type (enum), scheduled_at (timestamp), status (enum) |
| `NOTIFICATION_BATCH_ITEM` | id (PK, uuid), batch_id (FK, uuid), notification_id (FK, uuid), created_at (timestamp) |
| `DIGEST_SCHEDULE` | id (PK, uuid), user_id (FK, uuid), frequency (enum), timezone (string), next_send_at (timestamp) |
| `PUSH_SUBSCRIPTION` | id (PK, uuid), user_id (FK, uuid), endpoint (string), device_type (enum), is_active (boolean) |
| `NOTIFICATION_RULE` | id (PK, uuid), workspace_id (FK, uuid), event_type (enum), channel (enum), is_active (boolean) |

---

### 12. Reminder (`reminder`)
**Features:** Reminder schedule · Delivery · Templates · Snooze tracking

**Entities & Attributes:**

| Entity | Attributes |
|---|---|
| `REMINDER` | id (PK, uuid), user_id (FK, uuid), title (string), remind_at (timestamp), status (enum) |
| `REMINDER_DELIVERY` | id (PK, uuid), reminder_id (FK, uuid), channel (enum), status (enum), attempted_at (timestamp) |
| `REMINDER_TEMPLATE` | id (PK, uuid), workspace_id (FK, uuid), name (string), delivery_channel (enum), is_active (boolean) |
| `REMINDER_SNOOZE_LOG` | id (PK, uuid), reminder_id (FK, uuid), snoozed_by (FK, uuid), snoozed_until (timestamp), created_at (timestamp) |

---

### 13. Reports & Analytics (`insight`)
**Features:** Dashboards · Forms · Exports · Snapshots

**Entities & Attributes:**

| Entity | Attributes |
|---|---|
| `DASHBOARD` | id (PK, uuid), workspace_id (FK, uuid), name (string), owner_id (FK, uuid), is_shared (boolean) |
| `CHART_WIDGET` | id (PK, uuid), dashboard_id (FK, uuid), type (enum), config (json), pos_x (int) |
| `SAVED_VIEW` | id (PK, uuid), project_id (FK, uuid), name (string), filter_config (json), is_shared (boolean) |
| `FORM` | id (PK, uuid), project_id (FK, uuid), name (string), fields (json), is_published (boolean) |
| `FORM_SUBMISSION` | id (PK, uuid), form_id (FK, uuid), task_id (FK, uuid), data (json), submitted_at (timestamp) |
| `REPORT_EXPORT` | id (PK, uuid), workspace_id (FK, uuid), report_type (enum), format (enum), status (enum) |
| `KPI_TARGET` | id (PK, uuid), dashboard_id (FK, uuid), name (string), target_value (float), period (enum) |
| `REPORT_SNAPSHOT` | id (PK, uuid), dashboard_id (FK, uuid), snapshot_date (date), summary (json), generated_at (timestamp) |

---

### 14. Integration & API (`integration`)
**Features:** External connect · API key · Webhook · Sync logs

**Entities & Attributes:**

| Entity | Attributes |
|---|---|
| `INTEGRATION` | id (PK, uuid), workspace_id (FK, uuid), provider (enum), config (json), is_connected (boolean) |
| `API_KEY` | id (PK, uuid), workspace_id (FK, uuid), user_id (FK, uuid), name (string), expires_at (date) |
| `WEBHOOK` | id (PK, uuid), workspace_id (FK, uuid), url (string), events (json), is_active (boolean) |
| `WEBHOOK_DELIVERY` | id (PK, uuid), webhook_id (FK, uuid), event_type (enum), status (enum), attempted_at (timestamp) |
| `INTEGRATION_SYNC_LOG` | id (PK, uuid), integration_id (FK, uuid), sync_type (enum), status (enum), executed_at (timestamp) |

---

## Entity Relationships

| From | To | Relationship |
|---|---|---|
| WORKSPACE | USER | has |
| USER | ROLE | assigned |
| WORKSPACE | ACCESS_POLICY | enforces |
| USER | PASSWORD_RESET_TOKEN | resets |
| TEAM | TEAM_MEMBER | has |
| USER | TEAM_MEMBER | joins |
| WORKSPACE | DEPARTMENT | organizes |
| WORKSPACE | PROJECT | owns |
| PROJECT | PROJECT_MEMBER | has |
| PROJECT | EPIC | groups |
| PROJECT | MILESTONE | tracks |
| PROJECT | CHANGE_REQUEST | changes |
| PROJECT | SPRINT | has |
| SPRINT | TASK | contains |
| PROJECT | TASK | contains |
| TASK | TASK_ASSIGNEE | assigned |
| TASK | CHECKLIST_ITEM | has |
| TASK | TASK_DEPENDENCY | depends |
| TASK | TASK_LABEL | tagged |
| TASK | TASK_SUBMISSION | submits |
| TASK_SUBMISSION | TASK_SUBMISSION_FILE | includes |
| TASK | TASK_APPROVAL | approves |
| TASK | TASK_REOPEN_LOG | reopens |
| LABEL | TASK_LABEL | used |
| TASK | BUG_REPORT | linked |
| BUG_REPORT | BUG_REPRODUCTION_STEP | steps |
| BUG_REPORT | BUG_RESOLUTION | resolved |
| PROJECT | BOARD | has |
| BOARD | BOARD_VIEW | views |
| WORKSPACE | ROADMAP | owns |
| ROADMAP | ROADMAP_ITEM | items |
| VERSION | RELEASE_CALENDAR | plans |
| WORKSPACE | OBJECTIVE | sets |
| OBJECTIVE | KEY_RESULT | measured |
| KEY_RESULT | OKR_UPDATE | updates |
| OBJECTIVE | OKR_ALIGNMENT | aligns |
| OBJECTIVE | GOAL_CHECKIN | checkins |
| TASK | TIME_LOG | logs |
| USER | TIMESHEET | submits |
| TIMESHEET | TIMESHEET_ENTRY | entries |
| USER | OVERTIME_ENTRY | overtime |
| WORKSPACE | SKILL | defines |
| USER | USER_SKILL | has |
| PROJECT | RESOURCE_PLAN | allocates |
| RESOURCE_PLAN | RESOURCE_ALLOCATION_LOG | history |
| USER | CAPACITY_SNAPSHOT | capacity |
| WORKSPACE | CHANNEL | has |
| CHANNEL | CHANNEL_MEMBER | members |
| CHANNEL | MESSAGE | contains |
| MESSAGE | MESSAGE_REACTION | reacts |
| MESSAGE | MESSAGE_ATTACHMENT | files |
| MESSAGE | MESSAGE_READ_RECEIPT | reads |
| WORKSPACE | DIRECT_MESSAGE_CHANNEL | dm |
| DIRECT_MESSAGE_CHANNEL | DM_PARTICIPANT | participants |
| TASK | COMMENT | comments |
| COMMENT | REACTION | reacts |
| COMMENT | MENTION | mentions |
| TASK | ATTACHMENT | files |
| WORKSPACE | FILE_ASSET | stores |
| FILE_ASSET | FILE_VERSION | versions |
| FILE_ASSET | TASK_SUBMISSION_FILE | attached |
| DOCUMENT | DOCUMENT_VERSION | versions |
| DOCUMENT | DOCUMENT_APPROVAL | approval |
| TASK_APPROVAL | APPROVAL_COMMENT | discussion |
| PROJECT | WIKI_PAGE | wiki |
| WIKI_PAGE | WIKI_VERSION | versions |
| USER | NOTIFICATION | receives |
| NOTIFICATION | NOTIFICATION_DELIVERY | delivers |
| USER | NOTIFICATION_BATCH | batch |
| NOTIFICATION_BATCH | NOTIFICATION_BATCH_ITEM | items |
| WORKSPACE | NOTIFICATION_RULE | rules |
| USER | REMINDER | has |
| REMINDER | REMINDER_DELIVERY | delivers |
| REMINDER | REMINDER_SNOOZE_LOG | snoozes |
| WORKSPACE | DASHBOARD | owns |
| DASHBOARD | CHART_WIDGET | widgets |
| DASHBOARD | REPORT_SNAPSHOT | snapshots |
| PROJECT | FORM | forms |
| FORM | FORM_SUBMISSION | submits |
| WORKSPACE | REPORT_EXPORT | exports |
| WORKSPACE | INTEGRATION | connects |
| WORKSPACE | API_KEY | keys |
| WORKSPACE | WEBHOOK | webhooks |
| WEBHOOK | WEBHOOK_DELIVERY | delivery |
| INTEGRATION | INTEGRATION_SYNC_LOG | sync logs |

---

## Scenarios

### Task Lifecycle
Entities: `TASK`, `TASK_ASSIGNEE`, `CHECKLIST_ITEM`, `TASK_DEPENDENCY`, `TASK_LABEL`, `TASK_SUBMISSION`, `TASK_SUBMISSION_FILE`, `TASK_REOPEN_LOG`, `TIME_LOG`, `ACTIVITY_LOG`

### Approval
Entities: `TASK_APPROVAL`, `APPROVAL_COMMENT`, `TASK_SUBMISSION`, `BUG_RESOLUTION`, `CHANGE_REQUEST`, `DOCUMENT_APPROVAL`, `RELEASE_CALENDAR`

### File Management
Entities: `FILE_ASSET`, `FILE_VERSION`, `TASK_SUBMISSION_FILE`, `ATTACHMENT`, `MESSAGE_ATTACHMENT`, `DOCUMENT`, `DOCUMENT_VERSION`

### Notification
Entities: `NOTIFICATION`, `NOTIFICATION_DELIVERY`, `NOTIFICATION_BATCH`, `NOTIFICATION_BATCH_ITEM`, `NOTIFICATION_RULE`, `REMINDER`, `REMINDER_DELIVERY`, `REMINDER_TEMPLATE`, `REMINDER_SNOOZE_LOG`, `DIGEST_SCHEDULE`, `PUSH_SUBSCRIPTION`
