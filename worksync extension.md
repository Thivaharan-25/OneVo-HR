# 🔌 WorkSync IDE Extension — Data Flow & Integration Guide
> WorkSync-லிருந்து Extension-க்கு என்ன data வரும் · எப்படி work ஆகும் · Complete flow

---

## 📌 Big Picture — Overview

WorkSync Backend-ல் Chat Engine, Tasks Engine, Calendar Service, Reminder Scheduler ஆகிய நான்கு modules இருக்கும். இவை எல்லாம் ஒரே REST API + WebSocket layer வழியாக VS Code Extension-உடன் பேசும். Extension-ல் ஒரு Core இருக்கும் — அது Auth, WebSocket Client, Event Router, SQLite Cache எல்லாவற்றையும் handle பண்ணும். அந்த Core-லிருந்து Chat, Notifications, Reminders, Calendar என்று நான்கு Sidebar panels-க்கு data போகும்.

---

## 🔐 STEP 0 — Auth: Login Flow

**என்ன நடக்கும்:**

- Developer VS Code திறக்கிறார்
- Extension background-ல் automatically activate ஆகும்
- SecretStorage-ல் JWT token இருக்கா என்று check பண்ணும்
- **Token இருந்தால்:** Auto-login நடக்கும், WebSocket உடனே connect ஆகும்
- **Token இல்லாவிட்டால்:**
  - Sidebar-ல் Login form காட்டும்
  - Developer email + password enter பண்றார்
  - Backend-க்கு login request போகும்
  - Token + user details திரும்பி வரும்
  - Token-ஐ SecretStorage-ல் encrypted-ஆக save பண்ணும்
- WebSocket connection திறக்கும்
- எல்லா panels-க்கும் initial data load ஆகும்

**Login response-ல் என்ன வரும்:**

- JWT token (encrypted)
- User ID, பெயர், email, avatar
- Role (developer / manager / hr)
- Workspace ID மற்றும் workspace பெயர்

---

## 💬 PANEL 1 — Chat

### A. Channels List — Initial Load

- Extension sidebar திறந்தவுடன் backend-கிட்ட channels கேட்கும்
- Response-ல் developer join ஆன எல்லா channels வரும்
- ஒவ்வொரு channel-க்கும் பெயர், type (group / direct), unread count, கடைசி message காட்டும்
- உதாரணம்: `#general` group channel-ல் 3 unread, கடைசி message "John: Design review at 3pm"
- Direct message channels-ல் `John Doe` போன்ற person பெயர் காட்டும்

### B. Messages — Channel Select பண்ணும்போது

- Developer ஒரு channel click பண்றார்
- அந்த channel-ஓட கடைசி 50 messages backend-லிருந்து வரும்
- ஒவ்வொரு message-லும் sender பெயர், avatar, content, time காட்டும்
- Message-ல் `#task` tag இருந்தால் அது highlight ஆகும், pending status காட்டும்
- யார் யார் message படித்தார்கள் என்ற read receipt கூட வரும்

### C. New Message — Real-time (WebSocket)

- வேற யாராவது message அனுப்பினால் WebSocket வழியா extension-க்கு உடனே வரும்
- Event பெயர்: `chat.message.new`
- Sender பெயர், content, time — இவை Chat panel-ல் automatically append ஆகும்
- Page refresh தேவையில்லை — instant-ஆக காட்டும்

### D. Message Send — Developer பக்கம்

- Developer message type பண்ணி send பண்றார்
- Message backend-க்கு போகும்
- Backend response-ல் message ID, sent status வரும்
- Message-ல் `#task` tag இருந்தால் AI detected tag details கூட response-ல் வரும்
  - Task title, assignee, due date automatically parse ஆகும்

### E. AI Suggestion Card — Flow

Developer chat-ல் message type பண்ணும்போது AI automatically task detect பண்ணி suggestion card காட்டும்.

**என்ன நடக்கும் — step by step:**

- Developer chat-ல் `@john #task Fix login bug by tomorrow` என்று type பண்றார்
- Message send ஆகும்போது WorkSync backend AI அந்த message-ஐ scan பண்ணும்
- AI-யில் `#task` tag, assignee (`@john`), deadline (`tomorrow`) detect ஆகும்
- Backend WebSocket வழியாக Extension-க்கு `ai.suggestion` event push பண்ணும்
- Extension-ல் Chat panel-ல் ஒரு **Suggestion Card** pop-up ஆகும்:
  - Title: "Fix login bug"
  - Assigned to: John
  - Due date: Tomorrow (2026-04-28)
  - Project: proj_001
- Card-ல் இரண்டு buttons காட்டும்: **✅ Accept** மற்றும் **❌ Reject**
- Developer **Accept** click பண்ணினால்:
  - Backend-க்கு accept confirmation போகும்
  - WorkSync backend task automatically create பண்ணும்
  - John-க்கு notification போகும் ("New task assigned")
  - Calendar-ல் deadline auto-add ஆகும்
  - Chat Reminder list-ல் entry தெரியும்
- Developer **Reject** click பண்ணினால்:
  - Backend-க்கு reject confirmation போகும்
  - Suggestion card மறையும், task create ஆகாது
  - Message chat-ல் normal text-ஆகவே இருக்கும்

### F. Chat Reminder List

- Developer-ஓட chat reminders இரண்டு பிரிவில் காட்டும்
- **நான் create பண்ணியவை:** நான் யாரையாவது `@john #task` என்று assign பண்ணியது — அந்த status (in_progress / done) காட்டும்
- **என்னுக்கு assign ஆனவை:** வேற யாரோ என்னை `@arun #task` என்று assign பண்ணியது — due date, status காட்டும்

### Chat Panel — முழு Flow Summary

- Sidebar திறந்தவுடன் channels list load ஆகும்
- Channel click → messages load ஆகும்
- WebSocket listen தொடர்ந்து நடக்கும் — புதுசா message வந்தால் instant-ஆக காட்டும்
- Developer message type பண்ணி send பண்றார்
- `#tag` detect ஆனால் AI suggestion card தோன்றும்
- Accept click → task create ஆகும்
- Task created → project board + Chat Reminder list update ஆகும்

---

## 🔔 PANEL 2 — Notifications

### A. Notifications List — Initial Load

- Extension திறந்தவுடன் unread notifications list வரும்
- Notification types:
  - **task_assigned** — யாரோ உனக்கு task assign பண்ணினார் (priority: normal)
  - **task_approved** — Manager உன் task approve பண்ணினார் (priority: low)
  - **deadline_approaching** — நாளைக்கு deadline இருக்கு (priority: high)
  - **mention** — யாரோ chat-ல் உன்னை @mention பண்ணினார் (priority: normal)
- ஒவ்வொரு notification-க்கும் title, body, priority, time காட்டும்
- is_read: false → unread badge காட்டும்

### B. New Notification — Real-time (WebSocket)

- Manager எதாவது action எடுத்தால் WebSocket வழியா notification வரும்
- Event பெயர்: `notification.new`
- உதாரணம்: Manager task reject பண்ணினால் "Task returned" notification high priority-ல் வரும்
- Notification panel-ல் top-ல் prepend ஆகும்
- StatusBar badge number +1 ஆகும்
- High priority notification-ஆனால் VS Code-ல் popup காட்டும்

### C. Mark as Read

- Developer notification click பண்றார்
- Related task / chat message திறக்கும்
- Backend-க்கு read confirmation போகும்
- Badge count -1 ஆகும்

### Notifications Panel — முழு Flow Summary

- Extension திறந்தவுடன் unread notifications list காட்டும்
- StatusBar-ல் unread count badge காட்டும்
- WebSocket வழியா புதுசா notification வந்தால்:
  - List-ல் top-ல் தோன்றும்
  - Badge +1 ஆகும்
  - High priority ஆனால் VS Code popup காட்டும்
- Developer click பண்றார் → related task / chat திறக்கும் → mark as read ஆகும்

---

## ⏰ PANEL 3 — Reminders

### A. Reminders List

- Extension திறந்தவுடன் pending reminders list வரும்
- ஒவ்வொரு reminder-க்கும் title, due time, status (pending / snoozed) காட்டும்
- Source: manual (developer create பண்ணியது) அல்லது calendar (meeting reminder)
- Snoozed reminder-ஆனால் snooze_until time காட்டும்

### B. Reminder Fire — Real-time (WebSocket)

- Reminder time வந்தவுடன் backend WebSocket வழியா event அனுப்பும்
- Event பெயர்: `reminder.fire`
- VS Code-ல் popup காட்டும்: title + due time
- Popup-ல் இரண்டு options: **Snooze** (15 mins) அல்லது **Dismiss**

### C. Snooze

- Developer Snooze click பண்றார்
- Backend-க்கு snooze request போகும் (15 minutes)
- Response-ல் new snooze_until time வரும்
- 15 mins-ல் மறுபடியும் fire ஆகும்

### D. Dismiss

- Developer Dismiss click பண்றார்
- Backend-க்கு dismiss request போகும்
- Reminder list-லிருந்து remove ஆகும்

### Reminders Panel — முழு Flow Summary

- Extension start-ல் pending reminders list load ஆகும்
- Time வந்தவுடன் WebSocket event வரும் → VS Code popup தோன்றும்
- Snooze click → 15 mins கழித்து மறுபடியும் popup
- Dismiss click → reminder முடிந்தது, list-லிருந்து disappear ஆகும்

---

## 📅 PANEL 4 — Calendar

### A. Today's Events

- Developer Calendar panel திறக்கும்போது இன்றைய எல்லா events வரும்
- Event types:
  - **meeting** — Daily standup 09:00–09:30
  - **task_deadline** — Design homepage banner, due 17:00, priority high, status in_progress
  - **goal_milestone** — Q2 OKR checkpoint, EOD
  - **reminder** — Submit timesheet, 18:00
- ஒவ்வொரு event-க்கும் time, type, title காட்டும்

### B. Week View

- Developer week view select பண்றார்
- இந்த வாரம் முழுவதும் events வரும்
- ஒவ்வொரு நாளுக்கும் அன்றைய events list கிடைக்கும்

### C. Real-time Calendar Update (WebSocket)

- Manager புதுசா meeting schedule பண்ணினால் WebSocket event வரும்
- Event பெயர்: `calendar.event.added`
- Calendar panel-ல் automatically new event appear ஆகும் — refresh தேவையில்லை

### Calendar Panel — முழு Flow Summary

- Panel திறந்தவுடன் இன்றைய agenda load ஆகும்
- Events time order-ல் காட்டும்: meetings, deadlines, milestones, reminders
- Developer item click பண்றார் → related task / meeting / goal detail sidebar-ல் திறக்கும்
- Manager புதுசா event add பண்ணினால் WebSocket வழியா real-time-ல் calendar-ல் தெரியும்

---

## 🔄 2-Way Sync — எப்படி நடக்கும்

### Direction 1: Extension → WorkSync → Web App

- Developer VS Code-ல் task "Done" பண்றார்
- Extension backend-க்கு status update அனுப்பும்
- Backend DB-ல் update ஆகும்
- WebSocket வழியா Manager-ஓட Web App-க்கு broadcast போகும்
- Manager browser-ல் real-time-ல் task "Done" ஆனது காட்டும் ✅

### Direction 2: Web App → WorkSync → Extension

- Manager Web App-ல் new task assign பண்றார்
- Backend DB-ல் save ஆகும், notification create ஆகும்
- WebSocket push Developer-ஓட Extension-க்கு போகும்
- Extension-ல் நான்கு இடங்களில் உடனே update ஆகும்:
  - StatusBar badge +1 காட்டும்
  - VS Code popup: "John assigned: Design banner"
  - Calendar-ல் deadline auto-add ஆகும்
  - My Tasks panel-ல் new task appear ஆகும் ✅

---

## 📦 Extension-ல் Local Cache — என்ன store ஆகும்

Device-ல் SQLite database local-ஆக இருக்கும். Internet இல்லாவிட்டாலும் cached data காட்டும்.

| Table | என்ன store | Expiry |
|---|---|---|
| `jwt_token` | Auth token (encrypted) | Token expiry வரை |
| `channels` | Channel list | 1 hour |
| `messages` | Last 50 messages per channel | 24 hours |
| `notifications` | Last 20 notifications | 7 days |
| `calendar_events` | Today + next 7 days | 12 hours |
| `reminders` | All pending reminders | Until fired |
| `offline_queue` | Pending actions (offline) | Until synced |

### Offline Mode — எப்படி வேலை செய்யும்:

- Internet போனால் Extension cached data-லிருந்து காட்டும்
- User message send / status change பண்ணினால் offline_queue-ல் store ஆகும்
- Internet திரும்பி வந்தால்:
  - Queue-ல் இருந்த எல்லா actions sync ஆகும்
  - Fresh data pull ஆகும்
  - UI update ஆகும் ✅

---

## 🗂️ Complete API Reference — Extension use பண்றவை

### Auth
| Method | Endpoint | என்ன |
|---|---|---|
| POST | `/api/auth/login` | Login, JWT receive |
| POST | `/api/auth/refresh` | Token refresh |
| POST | `/api/auth/logout` | Logout, token invalidate |

### Chat
| Method | Endpoint | என்ன |
|---|---|---|
| GET | `/api/chat/channels` | My channels list |
| GET | `/api/chat/messages?channel_id=X` | Channel messages |
| POST | `/api/chat/message` | Message send |
| PATCH | `/api/chat/messages/{id}/read` | Mark read |
| GET | `/api/chat/reminders/me` | Chat reminder list |
| PATCH | `/api/chat/reminders/{id}/status` | Status update |
| POST | `/api/ai/suggestion/{id}/accept` | AI suggestion accept |
| POST | `/api/ai/suggestion/{id}/reject` | AI suggestion reject |

### Notifications
| Method | Endpoint | என்ன |
|---|---|---|
| GET | `/api/notifications/me` | My notifications |
| PATCH | `/api/notifications/{id}/read` | Mark read |
| POST | `/api/notifications/read-all` | All mark read |

### Reminders
| Method | Endpoint | என்ன |
|---|---|---|
| GET | `/api/reminders/me` | My reminders |
| POST | `/api/reminders/{id}/snooze` | Snooze |
| PATCH | `/api/reminders/{id}/dismiss` | Dismiss |

### Calendar
| Method | Endpoint | என்ன |
|---|---|---|
| GET | `/api/calendar/me?date=X` | Day events |
| GET | `/api/calendar/me?start=X&end=Y` | Week events |

### Tasks (My Space)
| Method | Endpoint | என்ன |
|---|---|---|
| GET | `/api/tasks/me` | My assigned tasks |
| PATCH | `/api/tasks/{id}/status` | Status update |
| POST | `/api/tasks/create` | New task create |

### WebSocket Events
| Event (Inbound) | என்ன |
|---|---|
| `chat.message.new` | New message arrived |
| `notification.new` | New notification |
| `reminder.fire` | Reminder time reached |
| `task.status.changed` | Task status updated by others |
| `calendar.event.added` | New calendar event |
| `ai.suggestion` | AI task suggestion ready |

| Event (Outbound) | என்ன |
|---|---|
| `chat.typing` | User typing indicator |
| `notification.read` | Notification read confirm |

---

## ⚡ Performance — எவ்வளவு வேகமாக load ஆகும்

**Extension start sequence:**

- VS Code திறந்தவுடன் JWT local-ஆக check ஆகும் — instant
- 500ms-க்குள் WebSocket connect ஆகும்
- Parallel-ஆக மூன்று calls ஒரே நேரத்தில் போகும்: notifications unread count, upcoming reminders, today's calendar
- StatusBar badge update ஆகும்
- **Total startup time: 1.5 seconds-க்கும் குறைவு**

**Panel open — first time:**
- Fresh API call போகும், data cache-ல் store ஆகும்

**Panel open — மறுபடியும்:**
- Cache-லிருந்து instantly காட்டும்
- Background-ல் fresh data pull ஆகும் (stale-while-revalidate)

**Real-time updates:**
- WebSocket push 100ms-க்கும் குறைவான latency-ல் வரும்

---

## 🔒 Security — Data எப்படி safe ஆக இருக்கும்

| Risk | Solution |
|---|---|
| Token leak | VS Code SecretStorage (OS-level encryption) |
| API intercept | HTTPS only, WSS only — plain HTTP reject |
| Cross-workspace | JWT-ல் workspace_id embed — server-side enforce |
| Cache leak | SQLite encrypted, device-local மட்டும் |
| Extension uninstall | Token + cache automatic wipe |
| Expired token | Auto-refresh → fail → re-login prompt |

---

## 👁️ Extension எதை பார்க்கும் — எதை பார்க்காது

### பார்க்கும் (WorkSync data மட்டும்):
- ✅ உங்கள் chat messages (WorkSync workspace-ல் மட்டும்)
- ✅ உங்களுக்கு assigned tasks
- ✅ உங்கள் calendar events
- ✅ உங்களுக்கான notifications
- ✅ உங்கள் reminders

### பார்க்காது (VS Code / Computer data):
- ❌ உங்கள் code files
- ❌ Keystrokes
- ❌ Terminal commands
- ❌ Other applications
- ❌ File system
- ❌ Git history
- ❌ Location / IP

---

## 🗺️ Build Order — இந்த sequence-ல் build பண்றது

**Week 1 — Foundation:**
- Extension scaffold setup (yo code)
- JWT login WebView உருவாக்கு
- SecretStorage-ல் token save பண்ண logic
- WebSocket connect + event router setup

**Week 2–3 — Chat Panel:**
- Channel list API + render
- Messages load + send
- `#tag` detect + AI suggestion card UI
- Accept / Reject flow → task create
- Real-time WebSocket message append

**Week 4 — Notifications:**
- GET notifications + render
- WebSocket `notification.new` handler
- StatusBar badge update logic
- VS Code popup (high priority notifications)
- Mark read + related item-க்கு navigate

**Week 5 — Reminders + Calendar:**
- GET reminders + list render
- WebSocket `reminder.fire` → popup
- Snooze / Dismiss API calls
- GET calendar events + render
- Calendar item click → detail open

**Week 6 — Polish + Publish:**
- Offline SQLite cache implement
- Error handling + retry logic
- Slack-style dark theme CSS
- `vsce package` + VS Code Marketplace publish
- Marketplace listing + description

---

*OneVo WorkSync IDE Extension — Data Flow & Integration Specification v1.0*
