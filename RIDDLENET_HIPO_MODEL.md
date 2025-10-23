# RiddleNet - Hierarchical Input-Process-Output (HIPO) Model

## System Overview
Network simulation learning platform with dual-namespace architecture for administrative and student operations.

---

## Level 0: System Overview

```
┌──────────────────────────────────────────────────────────┐
│                    RIDDLENET SYSTEM                      │
│                                                          │
│  INPUT               PROCESS              OUTPUT         │
│  ┌────────┐        ┌────────┐          ┌────────┐      │
│  │ Users  │        │ Engine │          │ Data   │      │
│  │ Data   │  ───▶  │ Logic  │  ───▶    │ Events │      │
│  │ Events │        │ State  │          │ Results│      │
│  └────────┘        └────────┘          └────────┘      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Level 1: Core Modules

### 1.1 Admin Module
```
INPUT                     PROCESS                   OUTPUT
┌──────────┐           ┌──────────┐             ┌──────────┐
│ Auth     │           │ Content  │             │ Config   │
│ Content  │  ───▶     │ User Mgmt│  ───▶       │ Analytics│
│ Config   │           │ Analytics│             │ Reports  │
└──────────┘           └──────────┘             └──────────┘
```

### 1.2 User Module
```
INPUT                     PROCESS                   OUTPUT
┌──────────┐           ┌──────────┐             ┌──────────┐
│ Login    │           │ Learning │             │ Progress │
│ Actions  │  ───▶     │ Simulate │  ───▶       │ Scores   │
│ Response │           │ Submit   │             │ Feedback │
└──────────┘           └──────────┘             └──────────┘
```

---

## Level 2: Subsystems

### 2.1 ADMIN SUBSYSTEMS

#### 2.1.1 Auth & Access
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Creds  │       │ Verify │         │ Token  │
│ Session│  ───▶ │ Role   │  ───▶   │ Access │
└────────┘       └────────┘         └────────┘
```

#### 2.1.2 Content Management
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Modules│       │ Builder│         │ Content│
│ Lessons│  ───▶ │ Publish│  ───▶   │ Library│
│ Sims   │       │ Version│         │ Catalog│
└────────┘       └────────┘         └────────┘
```

#### 2.1.3 Class Admin
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Roster │       │ Enroll │         │ Classes│
│ Assign │  ───▶ │ Assign │  ───▶   │ Sched  │
│ Config │       │ Track  │         │ Notify │
└────────┘       └────────┘         └────────┘
```

#### 2.1.4 Grading & Assessment
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Submit │       │ Grade  │         │ Scores │
│ Tests  │  ───▶ │ Review │  ───▶   │ Feedback│
│ Rubric │       │ Analyze│         │ Stats  │
└────────┘       └────────┘         └────────┘
```

#### 2.1.5 Analytics
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Activity│      │ Aggregate│       │ Reports│
│ Scores  │ ───▶ │ Visualize│ ───▶  │ Metrics│
│ Logs    │      │ Insights │       │ Charts │
└────────┘       └────────┘         └────────┘
```

---

### 2.2 USER SUBSYSTEMS

#### 2.2.1 Profile & Registration
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Account│       │ Validate│        │ Profile│
│ Prefs  │  ───▶ │ Enroll  │  ───▶  │ Access │
└────────┘       └────────┘         └────────┘
```

#### 2.2.2 Learning Interface
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Lessons│       │ Deliver │        │ Complete│
│ Sims   │  ───▶ │ Track   │  ───▶  │ Progress│
│ Resources│     │ Navigate│        │ Achieve │
└────────┘       └────────┘         └────────┘
```

#### 2.2.3 Simulation Engine
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Topology│      │ Simulate│        │ State  │
│ Config  │ ───▶ │ Execute │  ───▶  │ Valid  │
│ Commands│      │ Validate│        │ Results│
└────────┘       └────────┘         └────────┘
```

#### 2.2.4 Assessment
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Assign │       │ Submit │         │ Scores │
│ Tests  │  ───▶ │ Grade  │  ───▶   │ Progress│
│ Response│      │ Evaluate│        │ Feedback│
└────────┘       └────────┘         └────────┘
```

#### 2.2.5 Collaboration
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Messages│      │ Realtime│        │ Updates│
│ Teams   │ ───▶ │ Sync    │  ───▶  │ Chat   │
│ Share   │      │ Manage  │        │ Logs   │
└────────┘       └────────┘         └────────┘
```

---

## Level 3: Core Components

### 3.1 Data Layer
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ CRUD   │       │ Database│        │ Records│
│ Queries│  ───▶ │ ORM     │  ───▶  │ Relations│
│ Trans  │       │ Validate│        │ Integrity│
└────────┘       └────────┘         └────────┘

Models: User, Instructor, Class, Module, Lesson, 
        Simulation, Assignment, Submission, Score
```

### 3.2 Auth & Session
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Login  │       │ Verify  │        │ Token  │
│ Tokens │  ───▶ │ Session │  ───▶  │ Perms  │
│ Perms  │       │ RBAC    │        │ Security│
└────────┘       └────────┘         └────────┘

Features: Dual-namespace (admin/user), Split sessions,
          Role-based access, Session isolation
```

### 3.3 Simulation Engine
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Devices│       │ Network │        │ State  │
│ Topology│ ───▶ │ Emulate │  ───▶  │ Valid  │
│ CLI    │       │ Track   │        │ Diagnose│
└────────┘       └────────┘         └────────┘

Components: Device sim, Config engine, Topology manager,
            CLI interpreter, Validation system
```

### 3.4 Assessment System
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Work   │       │ Grade   │        │ Scores │
│ Tests  │  ───▶ │ Feedback│  ───▶  │ Analytics│
│ Rubrics│       │ Calculate│       │ Hints  │
└────────┘       └────────┘         └────────┘

Features: Auto-grading, Real-time feedback, 
          Progress tracking, Hint generation
```

### 3.5 Real-time Communication
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Messages│      │ WebSocket│       │ Updates│
│ Events  │ ───▶ │ Route    │  ───▶ │ Notify │
│ Notify  │      │ Sync     │       │ Broadcast│
└────────┘       └────────┘         └────────┘

Socket.IO: Presence tracking, Collaboration,
           Progress updates, Chat messaging
```

---

## Level 4: Support Services

### 4.1 File Management
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Uploads│       │ Storage │        │ URLs   │
│ Media  │  ───▶ │ Optimize│  ───▶  │ Access │
│ Docs   │       │ Serve   │        │ Download│
└────────┘       └────────┘         └────────┘
```

### 4.2 Notifications
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Events │       │ Generate│        │ Email  │
│ Triggers│ ───▶ │ Route   │  ───▶  │ In-app │
│ Templates│     │ Deliver │        │ Logs   │
└────────┘       └────────┘         └────────┘
```

### 4.3 Analytics
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Activity│      │ Aggregate│       │ Reports│
│ Metrics │ ───▶ │ Compute  │  ───▶ │ Dashboards│
│ Logs    │      │ Visualize│       │ Insights│
└────────┘       └────────┘         └────────┘
```

### 4.4 Deadlines
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Due    │       │ Enforce │        │ Reminders│
│ Extend │  ───▶ │ Notify  │  ───▶  │ Penalties│
│ Policy │       │ Track   │        │ Reports│
└────────┘       └────────┘         └────────┘
```

### 4.5 Import/Export
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Export │       │ Serialize│       │ Files  │
│ Import │  ───▶ │ Validate │  ───▶ │ Data   │
│ Config │       │ Transform│       │ Verify │
└────────┘       └────────┘         └────────┘
```

---

## System Integration

```
┌─────────────────────────────────────────────┐
│          SYSTEM DATA FLOW                   │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────┐        ┌──────┐                  │
│  │ Admin│◄──────►│ Core │                  │
│  │ Routes│       │Services│                 │
│  └──────┘        └──────┘                  │
│      │                │                     │
│      ▼                ▼                     │
│  ┌────────────────────────┐                │
│  │    Database (PostgreSQL)│               │
│  │  User, Class, Content  │               │
│  └────────────────────────┘                │
│      │                │                     │
│      ▼                ▼                     │
│  ┌──────┐        ┌──────┐                  │
│  │ User │◄──────►│ RT   │                  │
│  │ Routes│       │Services│                 │
│  └──────┘        └──────┘                  │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend
- **Framework**: Flask
- **Database**: PostgreSQL + SQLAlchemy
- **Real-time**: Socket.IO
- **Session**: Flask-Login + Split Sessions

### Frontend
- **Templates**: Jinja2
- **Styling**: Bootstrap 5
- **Scripts**: JavaScript + jQuery
- **Real-time**: Socket.IO Client

### Services
- **Auth**: Flask-Login + RBAC
- **Simulation**: Network emulation
- **Feedback**: Performance tracking
- **Analytics**: Data aggregation
- **Collaboration**: WebSocket
- **Files**: Werkzeug handlers

---

## Security & Performance

### Security
```
INPUT              PROCESS             OUTPUT
┌────────┐       ┌────────┐         ┌────────┐
│ Requests│      │ Auth    │        │ Access │
│ Creds   │ ───▶ │ Authorize│  ───▶ │ Audit  │
│ Data    │      │ Validate │       │ Encrypt│
└────────┘       └────────┘         └────────┘
```

### Performance
- Query optimization
- Session caching
- Media optimization
- Lazy loading
- Connection pooling

---

## Summary

Minimal HIPO model showing:
- **Dual-namespace architecture** (admin/user)
- **Multi-layer processing** (routes → services → data)
- **Real-time capabilities** (WebSocket)
- **Assessment system** (grading + analytics)
- **Scalable design** (concurrent users)

Complete ecosystem from content creation to assessment.
