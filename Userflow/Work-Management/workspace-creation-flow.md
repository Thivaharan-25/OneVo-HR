# Workspace Creation

**Area:** Work Workspace Creation  
**Required Permission:** `workspaces:create`; member management requires `workspaces:manage`

---

## Purpose

A workspace is a regular collaboration area for a group. It can hold members, chat, workspace-level resources, and projects. A workspace is not the same as a project, and it is not the source of truth for company reporting hierarchy.

Workspace members can come from:

| Source | Meaning | Creates employee record |
|:-------|:--------|:--------------------|
| Manual Invite | Selected employees/members receive a direct workspace invite and accept or decline | No |

---

## Preconditions

- Employee records exist and have active user links for workspace access.
- User has `workspaces:create`.
- User's active legal entity context is resolved before workspace creation.

---

## Flow Steps

### Step 1: Open Create Workspace

- **UI:** Work -> Workspaces -> Create Workspace
- **Backend:** Checks module entitlement and `workspaces:create`.
- **Context:** Active legal entity is shown as read-only context.

### Step 2: Invite Initial Members

1. User searches active employees/members in the current tenant and permitted Company context.
2. System validates the actor has authority to invite members in the selected Company context.
3. Selected members receive direct invitations and accept or decline.
4. Phase 1 does not use workspace source pools, owner-to-owner participation requests, or linked workspace membership pools.

### Step 3: Assign Workspace Roles

- **UI:** User assigns local workspace roles: Admin/Lead, Member, or Viewer.
- **Rule:** These are local workspace roles. They do not grant tenant-wide HR, payroll, security, billing, or project visibility.
- **Validation:** User cannot assign a role they are not allowed to grant.

### Step 4: Save Workspace

- **DB:** `workspaces`, `workspace_roles`, `workspace_members`.

### Step 5: Add Member Later

- **UI:** Workspace Settings -> Members -> Invite.
- Search is filtered by the user's active Company context and member-management authority.
- The selected member receives a direct invite and accepts or declines.
- On acceptance, ONEVO adds the employee-backed user as a workspace member.

---

## Project Link From Workspace

When a workspace authority holder creates a project from a workspace:

1. User clicks Create Project from workspace.
2. System checks `projects:create` plus local workspace authority.
3. Project owning legal entity is set from active legal entity context.
4. Creator becomes project admin.
5. Project stores the workspace as its single `workspace_id`.
6. Project opens with Kanban, List, and Calendar views for its work items.

Simple project-link invitations are handled between project admins. They create project-link records after acceptance; they do not link workspaces or create workspace source pools in Phase 1.

---

## Visibility Rules

- Workspace Admin/Lead sees workspace progress, members, tasks, blockers, and project links for this workspace.
- Workspace Member sees workspace resources and their own/project-visible work.
- Workspace Viewer sees read-only workspace content allowed by workspace policy.
- Reporting-manager relationship does not grant control over that employee inside another user's workspace.

---

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| User lacks `workspaces:create` | Blocked | "You do not have permission to create workspaces" |
| Selected employee outside authority | Invite blocked | "You do not have permission to invite this member in the selected Company context" |

---

## Related

- [[modules/work-management/foundation/overview|Work Foundation]]
- [[modules/org-structure/positions/overview|Positions]]
- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/task-flow|Task Management]]
