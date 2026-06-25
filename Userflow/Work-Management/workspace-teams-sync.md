
**Area:** Work Workspace Creation (Phase 2)
**Trigger:** User creates or edits a workspace

---

## Purpose

Allows a workspace admin to connect a Work workspace with Microsoft Teams in Phase 2. The admin can create a new Microsoft Team during workspace creation or link an existing Team that has the same or similar members.

---


1. User opens Create Workspace.
2. User enters workspace name, slug, description, and members.
3. UI shows a checkbox: "Create Microsoft Teams group for this workspace".
6. User submits.
7. ONEVO creates the workspace.

---


1. User opens Workspace Settings -> Integrations -> Microsoft Teams.
5. UI displays candidates:
   - exact match
   - partial match
7. ONEVO stores `workspace_teams_links`.
9. ONEVO starts webhook/delta sync.

---

## Message Sync Experience

| User Action | Expected Result |
|:------------|:----------------|
| Sync fails | Message remains visible in ONEVO with sync warning and retry action |

---

## Edge Cases


---

## Related

- [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]]
- [[modules/work-management/foundation/overview|Work Foundation]]
- [[Userflow/Chat/chat-overview|Chat]]
