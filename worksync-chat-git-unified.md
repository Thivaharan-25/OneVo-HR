# 💬 WorkSync Chat + Git Monitor — Unified Flow
> Web App Chat + IDE Extension Chat = Same Chat · Git Activity automatic-ஆ Chat-ல வரும்

---

## 📌 Core Idea — ஒரே line-ல

```
WorkSync Chat (Web App) ══════════════════════ WorkSync Chat (VS Code)
         ║                                              ║
         ╚══════════════╦═══════════════════════════════╝
                        ║
                 WorkSync Backend
                 (Single source of truth)
                        ║
                   Git Activity
              (Commits, Branches, PRs, CI/CD)
                        ║
                   Auto-ஆ Chat-ல வரும்
```

**Manager Web-ல பார்க்கிறார் = Developer VS Code-ல பார்க்கிறார் = Same Chat.**

---

## 🔄 Chat Sync — எப்படி work ஆகும்

### One Backend, Two Clients

```
┌─────────────────┐         ┌─────────────────────┐
│  Web App Chat   │         │  VS Code Extension  │
│  (Manager/HR/  │         │  Chat Panel         │
│   Team Lead)   │         │  (Developer)        │
└────────┬────────┘         └──────────┬──────────┘
         │                             │
         │    HTTPS + WebSocket        │
         └──────────────┬──────────────┘
                        │
               ┌────────▼────────┐
               │ WorkSync Backend │
               │                 │
               │ • Chat Engine   │
               │ • Message Store │
               │ • WebSocket Hub │
               └────────┬────────┘
                        │
              ┌─────────▼──────────┐
              │   Git Activity     │
              │ (GitHub Webhook +  │
              │  VS Code Git API)  │
              └────────────────────┘
```

### Real-time Sync Flow

```
Manager → Web App-ல message type பண்றார்
                    ↓
POST /api/chat/message → Backend receive
                    ↓
Backend → WebSocket broadcast:
  ├── Web App-ல இருக்கற எல்லாருக்கும் ✅
  └── VS Code Extension-ல இருக்கற எல்லாருக்கும் ✅
                    ↓
Developer → VS Code sidebar-ல உடனே தெரியும் (< 100ms)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Developer → VS Code-ல reply பண்றார்
                    ↓
POST /api/chat/message → Backend receive
                    ↓
Backend → WebSocket broadcast:
  ├── Manager Web App-ல உடனே தெரியும் ✅
  └── மற்ற VS Code users-க்கும் தெரியும் ✅
```

---

## 🐙 Git Activity → Chat — எப்படி வருது

### எந்த Git event → எந்த Chat message

#### 3. Pull Request

```
Developer → GitHub-ல PR raise பண்றார்
                    ↓
GitHub Webhook → WorkSync Backend
                    ↓
┌─────────────────────────────────────────┐
│ 🤖 WorkSync                             │
│ 🔀 PR #42 opened by Arun               │
│ "Fix login bug"                         │
│ feature/task-123-fix → main             │
│ [Review PR] 11:00 AM                   │
└─────────────────────────────────────────┘
```

#### 4. CI/CD Result

```
GitHub Actions run → complete
                    ↓
GitHub Webhook → WorkSync Backend
                    ↓
Pass ஆனால்:
┌─────────────────────────────────────────┐
│ 🤖 WorkSync                             │
│ ✅ CI Passed — PR #42                   │
│ All checks passed · Ready to merge      │
│ 11:45 AM                                │
└─────────────────────────────────────────┘

Fail ஆனால்:
┌─────────────────────────────────────────┐
│ 🤖 WorkSync                             │
│ ❌ CI Failed — PR #42                   │
│ Failed: Unit Tests, Lint                │
│ [View Logs] 11:45 AM                   │
└─────────────────────────────────────────┘
```

#### 5. PR Merged

```
┌─────────────────────────────────────────┐
│ 🤖 WorkSync                             │
│ 🎉 PR #42 merged to main               │
│ Task status → Done automatically        │
│ 14:30 PM                                │
└─────────────────────────────────────────┘
```

#### 6. Branch Warning

```
Wrong branch detect:
┌─────────────────────────────────────────┐
│ 🤖 WorkSync                             │
│ ⚠️ Branch naming mismatch              │
│ Current:  my-random-branch             │
│ Expected: feature/task-123-*           │
│ [Rename] 09:20 AM                      │
└─────────────────────────────────────────┘
```

---

## 💬 Chat Channels — எப்படி organize ஆகும்

### Channel Types

```
Workspace
├── #general          ← எல்லாரும் chat பண்றது
├── #announcements    ← Admin/Manager posts மட்டும்
├── #sprint-42        ← Sprint-specific
│
├── Task Channels (auto-create):
│   ├── #task-123-fix-login-bug     ← task create ஆனவுடன்
│   ├── #task-124-design-banner     ← auto channel
│   └── #task-125-api-integration
│
└── Direct Messages
    ├── Arun ↔ John
    └── Arun ↔ Priya
```

### Task Channel — என்ன தெரியும்

```
#task-123-fix-login-bug
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 Task created: Fix login bug
   Assigned: Arun · Due: Apr 28 · High 🔴
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌿 Arun created branch: feature/task-123-fix
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 John: "Check the auth middleware first"
💬 Arun: "Got it, looking now"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔨 Arun committed: "Fix JWT validation"
🔨 Arun committed: "Add error handling"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔀 PR #42 opened by Arun → [Review PR]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ CI Passed — PR #42
💬 John: "LGTM! Approved 👍"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 PR merged · Task → Done ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Web App-லயும் இதே ✅
VS Code-லயும் இதே ✅
```

---

## 🌐 Web App vs VS Code — என்ன வித்தியாசம்

| | Web App Chat | VS Code Chat |
|---|---|---|
| **யாரு use பண்றாங்க** | Manager, HR, Team Lead | Developer |
| **Message data** | Same ✅ | Same ✅ |
| **Channels** | Same ✅ | Same ✅ |
| **Git auto messages** | தெரியும் ✅ | தெரியும் ✅ |
| **Real-time** | ✅ | ✅ |
| **#task AI tag** | ✅ | ✅ |
| **Extra** | Full browser UI | Sidebar + Git monitor |

**Data ஒண்ணுதான் — பார்க்கிற இடம் மட்டும் வேற.**

---

## 📅 Real Day — Complete Flow

```
09:00 — Manager (Web App):
  💬 "Team, sprint starts today. Arun fix login bug first"

09:00 — Arun (VS Code sidebar):
  உடனே தெரியும் ✅
  💬 "On it!"

11:00 — Arun PR raise:
  🔀 PR #42 opened → [Review PR]
  → Manager Web App-ல click பண்ணி review பண்றார்
  💬 "Two small comments, check line 45"

11:15 — Arun (VS Code):
  💬 "Fixed, force pushed"
  🔨 Committed: "Address review comments"

11:30 — CI Run:
  ✅ CI Passed — PR #42
  → Manager Web App-ல தெரியும்
  💬 "Approved! Merge it"

11:45 — PR Merged:
  🎉 Merged to main
  🤖 Task status → Done automatically
  → Timesheet updated ✅
  → Manager dashboard updated ✅
```

**Developer VS Code விட்டு போகலை.**
**Manager browser விட்டு போகலை.**
**இரண்டும் same chat-ல இருந்தாங்க.** ✅

---

## ⚙️ Technical — எப்படி build ஆகும்

### Backend — ஒரே WebSocket Hub

```
WorkSync Backend
       │
  Socket.io Server
       │
  ┌────┴────┐
  │  Rooms  │
  │         │
  │ ch_001  │ ← #general
  │ ch_002  │ ← #task-123
  │ ch_003  │ ← DM: Arun-John
  └────┬────┘
       │
  누가 emit பண்ணினாலும்
  (Web App or VS Code)
  அந்த room-ல இருக்கற
  எல்லாருக்கும் broadcast
```

### Web App — React

```javascript
// Socket connect
const socket = io('wss://api.worksync.io', {
  auth: { token: jwt }
});

// Message receive
socket.on('chat.message.new', (msg) => {
  setMessages(prev => [...prev, msg]);
});

// Message send
socket.emit('chat.message.send', {
  channel_id: 'ch_002',
  content: 'Fix the auth middleware'
});
```

### VS Code Extension — TypeScript

```typescript
// Same socket logic — different UI
const socket = io('wss://api.worksync.io', {
  auth: { token: await secretStorage.get('jwt') }
});

// Message receive → WebView update
socket.on('chat.message.new', (msg) => {
  chatPanel.webview.postMessage({
    type: 'NEW_MESSAGE',
    data: msg
  });
});

// Git commit detect → chat auto message
vscode.workspace.onDidSaveTextDocument(() => {
  const repo = gitExtension.getRepository(uri);
  // commit detect பண்ணி backend-க்கு அனுப்பு
});
```

---

## 📦 Data Flow Summary

```
எந்த event                 எங்கிருந்து          Chat-ல என்ன வரும்
──────────────────────────────────────────────────────────────────
Team message          Web App / VS Code    💬 Normal message
PR opened             GitHub Webhook       🔀 PR card + link
CI Pass               GitHub Webhook       ✅ CI passed card
CI Fail               GitHub Webhook       ❌ CI failed + logs
PR Merged             GitHub Webhook       🎉 Merged card
Branch warning        VS Code Git API      ⚠️ Warning card
Task created          WorkSync Backend     🤖 Task card
Task done             WorkSync Backend     ✅ Done card
```

---

## 🎯 Summary

```
WorkSync Chat
    = Web App Chat (Manager/HR/Lead பார்க்கிறார்)
    + VS Code Chat (Developer பார்க்கிறார்)
    + Git Activity Auto Messages
    ──────────────────────────────
    = ஒரே conversation, எல்லாரும் ஒரே page-ல

Developer code பண்றார் → Git activity → Chat-ல தெரியும்
Manager Web-ல பார்க்கிறார் → same chat → progress தெரியும்
Switch பண்ண வேண்டாம் · Form fill வேண்டாம் · Manual update வேண்டாம்
```

---

*OneVo WorkSync — Chat + Git Monitor Unified Specification v1.0*
