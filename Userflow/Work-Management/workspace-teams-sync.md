# Workspace Teams Sync

**Area:** WorkSync Workspace Creation
**Trigger:** User creates or edits a workspace
**Required Permission:** `workspaces:create` for creation, `workspaces:manage` for Teams linking

---

## Purpose

Allows a workspace admin to connect a WorkSync workspace with Microsoft Teams. The admin can create a new Microsoft Team during workspace creation or link an existing Team that has the same or similar members.

---

## Create Workspace With New Teams Group

1. User opens Create Workspace.
2. User enters workspace name, slug, description, and members.
3. UI shows a checkbox: "Create Microsoft Teams group for this workspace".
4. If checked, ONEVO validates Teams readiness:
   - tenant Teams integration enabled
   - creator has linked Teams account
   - workspace members have linked Teams accounts
   - creator has permission to create/link Teams groups
5. If not all members are linked, UI shows missing members and disables Team creation unless tenant policy allows partial sync.
6. User submits.
7. ONEVO creates the workspace.
8. ONEVO creates the Microsoft Team and adds mapped members.
9. ONEVO stores the workspace-to-Team link and creates/links the default chat channel.
10. Workspace opens with a Teams sync status indicator.

---

## Link Existing Teams Group

1. User opens Workspace Settings -> Integrations -> Microsoft Teams.
2. User clicks "Sync existing Teams group".
3. ONEVO searches Teams visible to the user/admin.
4. ONEVO compares each Team's members to workspace members.
5. UI displays candidates:
   - exact match
   - partial match
   - extra Teams members
   - missing Teams members
6. User selects a Team and confirms member differences.
7. ONEVO stores `workspace_teams_links`.
8. ONEVO links matching channels or asks user which ONEVO channel maps to which Teams channel.
9. ONEVO starts webhook/delta sync.

---

## Message Sync Experience

| User Action | Expected Result |
|:------------|:----------------|
| User sends message in ONEVO linked channel | Message appears in Teams |
| User sends message in linked Teams channel | Message appears in ONEVO |
| User edits/deletes in Teams | ONEVO reflects edit/delete when Graph allows it |
| User edits/deletes in ONEVO | Teams reflects change when policy and Graph permissions allow it |
| Sync fails | Message remains visible in ONEVO with sync warning and retry action |

---

## Edge Cases

- If a workspace member has no Teams connection, ONEVO shows them as missing from Teams sync.
- If existing Teams group contains extra users, ONEVO warns before linking.
- ONEVO does not auto-create ONEVO accounts for external Teams users.
- Private Teams chat sync can be disabled while Teams channel sync remains enabled.
- Teams outage does not block ONEVO workspace creation; the Teams link moves to failed/retry state.

---

## Related

- [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]]
- [[modules/work-management/foundation/overview|WorkSync Foundation]]
- [[modules/work-management/chat/teams-sync/end-to-end-logic|Teams Chat Sync Logic]]
- [[Userflow/Chat/chat-overview|Chat]]
