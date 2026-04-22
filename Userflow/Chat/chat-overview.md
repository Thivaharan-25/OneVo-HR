# Chat

**Area:** Chat pillar (`/chat`)  
**Trigger:** User clicks the Chat icon on the icon rail  
**Required Permission:** `chat:read` (view channels); `chat:write` (send messages)

## Purpose

Chat is real-time team communication within ONEVO. It is a first-class pillar — not nested inside Workforce — because communication happens across HR, project, and org contexts. Channels can be tied to projects, teams, or be open workspace-wide.

## Key Entities

| Entity | Role |
|---|---|
| `CHANNEL` | A named conversation space — public, private, or project-linked |
| `CHANNEL_MEMBER` | User-to-channel membership with role |
| `MESSAGE` | A single chat message with optional attachments and reactions |
| `MESSAGE_REACTION` | Emoji reaction on a message |
| `MESSAGE_ATTACHMENT` | File attached to a message (linked to `FILE_ASSET`) |
| `DIRECT_MESSAGE_CHANNEL` | A private 1:1 or group DM conversation |
| `DM_PARTICIPANT` | Members of a DM conversation |
| `MESSAGE_READ_RECEIPT` | Tracks who has read which messages |

## Flow Steps

### View Channels (`/chat`)
1. User opens the Chat pillar
2. System loads the sidebar of channels the user is a member of, grouped:
   - **Direct Messages** — 1:1 and group DMs
   - **Channels** — workspace public channels and private channels user belongs to
3. Unread channels are bolded with an unread count badge
4. User clicks a channel to open its message thread

### Send a Message
1. User opens a channel or DM
2. User types in the message input and presses Enter (or clicks Send)
3. System creates a `MESSAGE` record and delivers it to all channel members via SignalR
4. `MESSAGE_READ_RECEIPT` is created for the sender; others receive receipts as they view

### Create a Channel
1. User clicks "+ New Channel" (requires `chat:write`)
2. User enters: channel name, description, type (public / private)
3. User optionally links the channel to a WMS project
4. System creates `CHANNEL` and adds the creator as a member with role "admin"
5. User invites other members

### Start a Direct Message
1. User clicks "+ New DM"
2. User searches for one or more employees within the entity scope
3. System creates `DIRECT_MESSAGE_CHANNEL` and `DM_PARTICIPANT` records
4. Conversation opens immediately

### React to a Message
1. User hovers over a message and clicks the emoji picker
2. User selects an emoji — system creates `MESSAGE_REACTION`
3. Reaction appears on the message with a count; clicking again removes it

### Attach a File
1. User clicks the attachment icon in the message input
2. User uploads a file — system creates `FILE_ASSET` and `MESSAGE_ATTACHMENT` records
3. Attachment is displayed inline in the message thread

## Connection Points

| Connects to | How |
|---|---|
| Workforce → Projects | A channel can be linked to a WMS project for project-specific communication |
| People → Employees | DM participants are ONEVO employees — name and avatar from their profile |
| Inbox | @mentions in a channel message create an Inbox notification for the mentioned user |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/task-flow|Task Management]]
