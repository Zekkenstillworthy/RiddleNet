# RiddleNet Application - Data Flow Diagram

## System Overview
RiddleNet is a comprehensive network simulation and learning management platform with dual-module architecture supporting both learner and instructor workflows.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          RiddleNet Platform                          │
│                    (Flask + SocketIO + SQLAlchemy)                  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
          ┌─────────▼─────────┐         ┌──────────▼──────────┐
          │   Learner Module   │         │  Instructor Module  │
          │    (User Space)    │         │   (Admin Space)     │
          └─────────┬─────────┘         └──────────┬──────────┘
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │     Database Layer (MySQL)    │
                    │  - Learner Data               │
                    │  - Instructor Data            │
                    │  - Content & Progress         │
                    │  - Collaboration & Messaging  │
                    └───────────────────────────────┘
```

---

## Detailed Module Flow

### 1. **Learner Module Data Flow**

```
User Access
    │
    ├─→ Authentication Layer
    │       │
    │       ├─→ Login/Signup (user.views)
    │       └─→ Session Management (Flask-Login)
    │
    ├─→ Learning Interface
    │       │
    │       ├─→ Dashboard (user.views)
    │       │       └─→ Progress Overview
    │       │       └─→ Assigned Tasks
    │       │       └─→ Class Enrollment
    │       │
    │       ├─→ Class Access (universal_class_routes)
    │       │       └─→ Modules & Lessons
    │       │       └─→ Assignments
    │       │       └─→ Announcements
    │       │
    │       ├─→ Simulation Environment (dynamic_simulation_routes)
    │       │       └─→ Network Topology Builder
    │       │       └─→ Device Configuration
    │       │       └─→ CLI Emulator
    │       │       └─→ Real-time Validation
    │       │
    │       ├─→ Assessment System (quiz_routes)
    │       │       └─→ Question Groups
    │       │       └─→ Answer Submission
    │       │       └─→ Scoring & Feedback
    │       │
    │       └─→ Troubleshooting Labs (troubleshooting_routes)
    │               └─→ Scenario Loading
    │               └─→ Problem Diagnosis
    │               └─→ Solution Submission
    │
    ├─→ Collaboration Features
    │       │
    │       ├─→ Real-time Chat (collaborative_troubleshooting_api)
    │       ├─→ Team Lobbies (collaboration_service)
    │       ├─→ Shared Workspaces
    │       └─→ Peer Messaging
    │
    ├─→ Progress Tracking
    │       │
    │       ├─→ Topology Progress (topology_progress_api)
    │       ├─→ Simulation Attempts (SimulationProgress)
    │       ├─→ Quiz Scores (Score)
    │       └─→ Achievement Badges (badge_service)
    │
    └─→ Notification System
            │
            ├─→ Assignment Alerts (notification_routes)
            ├─→ Deadline Reminders
            ├─→ Instructor Announcements
            └─→ WebSocket Updates (socket_manager)
```

### 2. **Instructor Module Data Flow**

```
Instructor Access
    │
    ├─→ Authentication Layer
    │       │
    │       ├─→ Admin Login (auth_controller)
    │       └─→ Namespace Isolation (session security)
    │
    ├─→ Content Management
    │       │
    │       ├─→ Class Management (class_controller)
    │       │       └─→ Create/Edit Classes
    │       │       └─→ Enroll Learners
    │       │       └─→ Class Settings
    │       │
    │       ├─→ Module Creation (enhanced_module_controller)
    │       │       └─→ Learning Modules
    │       │       └─→ Lesson Editor
    │       │       └─→ Content Sequencing
    │       │
    │       ├─→ Simulation Builder (simulation_routes)
    │       │       └─→ Topology Design
    │       │       └─→ Task Configuration
    │       │       └─→ Validation Rules
    │       │       └─→ RNet File Management
    │       │
    │       ├─→ Assessment Design (question_group_controller)
    │       │       └─→ Question Banks
    │       │       └─→ Quiz Builder
    │       │       └─→ Rubric Creation
    │       │
    │       └─→ Lab Scenarios (instructor_lab_controller)
    │               └─→ Troubleshooting Setup
    │               └─→ Challenge Configuration
    │               └─→ Anti-Cheat Measures
    │
    ├─→ Assignment Management
    │       │
    │       ├─→ Task Assignment (task_assignment)
    │       ├─→ Simulation Assignment (simulation_assignment)
    │       ├─→ Deadline Policies (deadline_service)
    │       └─→ Submission Tracking (assignment_submission)
    │
    ├─→ Monitoring & Analytics
    │       │
    │       ├─→ Dashboard Overview (dashboard_controller)
    │       │       └─→ Learner Statistics
    │       │       └─→ Progress Reports
    │       │       └─→ Activity Logs
    │       │
    │       ├─→ Score Management (score_controller)
    │       │       └─→ Grade Review
    │       │       └─→ Performance Analytics
    │       │       └─→ Export Reports
    │       │
    │       ├─→ Real-time Monitoring (socket_manager)
    │       │       └─→ Active Learners
    │       │       └─→ Live Progress
    │       │       └─→ System Events
    │       │
    │       └─→ Audit Logs (audit_log_controller)
    │               └─→ User Activity
    │               └─→ System Changes
    │               └─→ Security Events
    │
    ├─→ Communication Tools
    │       │
    │       ├─→ Announcements (notification_controller)
    │       ├─→ Direct Messaging
    │       ├─→ Class Broadcasts
    │       └─→ Email Notifications
    │
    └─→ User Management
            │
            ├─→ Learner Accounts (user_controller)
            ├─→ Role Assignments
            ├─→ Access Control
            └─→ Profile Management
```

---

## Core System Components

### 3. **Database Layer Architecture**

```
Database (MySQL)
    │
    ├─→ User Management Tables
    │       ├─→ users (Learner accounts)
    │       ├─→ instructors (Instructor accounts)
    │       ├─→ class_students (Enrollment mapping)
    │       └─→ user_notifications (Alert system)
    │
    ├─→ Content Tables
    │       ├─→ classes (Course definitions)
    │       ├─→ modules (Learning units)
    │       ├─→ lessons (Content blocks)
    │       ├─→ simulations (Network labs)
    │       ├─→ troubleshooting (Problem scenarios)
    │       └─→ question_groups (Assessment items)
    │
    ├─→ Progress Tracking Tables
    │       ├─→ scores (Assessment results)
    │       ├─→ topology_progress (Network builds)
    │       ├─→ simulation_progress (Lab attempts)
    │       ├─→ simulation_attempts (Submission history)
    │       ├─→ troubleshooting_progress (Problem solving)
    │       └─→ lesson_progress (Content completion)
    │
    ├─→ Assignment Tables
    │       ├─→ task_assignments (Task distribution)
    │       ├─→ simulation_assignments (Lab assignments)
    │       ├─→ assignment_submissions (Learner work)
    │       └─→ deadline_policies (Due dates)
    │
    ├─→ Collaboration Tables
    │       ├─→ collaboration_lobbies (Team spaces)
    │       ├─→ lobby_participants (Team members)
    │       ├─→ lobby_chat_messages (Team chat)
    │       ├─→ lobby_device_locks (Resource locking)
    │       └─→ team_chat_messages (Group communication)
    │
    ├─→ Gamification Tables
    │       ├─→ user_badges (Achievements)
    │       ├─→ challenge_progress (Challenge tracking)
    │       ├─→ challenge_scores (Challenge results)
    │       └─→ point_transactions (Reward system)
    │
    └─→ System Tables
            ├─→ activity_logs (Audit trail)
            ├─→ scenario_timers (Session tracking)
            ├─→ notification_history (Communication log)
            └─→ admin_settings (Configuration)
```

---

## API & Communication Flow

### 4. **Real-time Communication (WebSocket)**

```
Client Browser
    │
    ├─→ WebSocket Connection (socket_manager.py)
    │       │
    │       ├─→ Authentication Check
    │       │       └─→ Learner: join user_{id} room
    │       │       └─→ Instructor: join admin_room
    │       │
    │       ├─→ Event Handlers
    │       │       ├─→ connect/disconnect
    │       │       ├─→ health_check
    │       │       ├─→ join_dashboard
    │       │       └─→ get_admin_user_list
    │       │
    │       └─→ Broadcast Channels
    │               ├─→ all_users (Platform-wide)
    │               ├─→ admin_room (Instructor-only)
    │               ├─→ user_{id} (Individual learner)
    │               └─→ announcements (Notification channel)
    │
    └─→ Real-time Events
            ├─→ Assignment notifications
            ├─→ Progress updates
            ├─→ Chat messages
            ├─→ Collaboration locks
            └─→ System alerts
```

### 5. **REST API Flow**

```
HTTP Requests
    │
    ├─→ Learner APIs (/api/*)
    │       ├─→ /api/topology/progress (Topology tracking)
    │       ├─→ /api/simulations (Lab access)
    │       ├─→ /api/quiz (Assessment submission)
    │       ├─→ /api/feedback (Performance data)
    │       └─→ /api/collaboration (Team features)
    │
    ├─→ Instructor APIs (/instructor/api/*)
    │       ├─→ /instructor/api/classes (Class management)
    │       ├─→ /instructor/api/deadlines (Due date management)
    │       ├─→ /instructor/api/scores (Grade access)
    │       └─→ /instructor/api/analytics (Reporting)
    │
    ├─→ Dynamic Simulation APIs (/dynamic/*)
    │       ├─→ /dynamic/simulation/{id} (Lab launcher)
    │       ├─→ /dynamic/submit (Solution validation)
    │       ├─→ /dynamic/progress (State persistence)
    │       └─→ /dynamic/feedback (Real-time hints)
    │
    └─→ Topology APIs (/admin/topology/*)
            ├─→ /admin/topology/create (Builder tool)
            ├─→ /admin/topology/validate (Design check)
            └─→ /admin/topology/export (RNet generation)
```

---

## Service Layer Architecture

### 6. **Business Logic Services**

```
Services Layer
    │
    ├─→ Simulation Services
    │       ├─→ database_simulation_service (Lab loading)
    │       ├─→ gamified_topology_service (Interactive builds)
    │       ├─→ rnet_file_service (Topology storage)
    │       ├─→ rnet_validation_service (Design validation)
    │       └─→ rnet_version_control_service (Change tracking)
    │
    ├─→ Collaboration Services
    │       ├─→ collaboration_service (Team coordination)
    │       ├─→ troubleshooting_lobbies (Problem-solving spaces)
    │       └─→ team_chat_service (Group messaging)
    │
    ├─→ Assessment Services
    │       ├─→ feedback_service (Performance analysis)
    │       ├─→ progression_service (Learning path tracking)
    │       └─→ badge_service (Achievement system)
    │
    ├─→ Management Services
    │       ├─→ deadline_service (Due date enforcement)
    │       ├─→ notification_service (Alert distribution)
    │       ├─→ credential_service (Authentication helpers)
    │       └─→ mode_service (Feature toggling)
    │
    └─→ Integration Services
            ├─→ assignment_service (Task distribution)
            ├─→ qr_service (Code generation)
            └─→ class_template_generator (Dynamic routing)
```

---

## Security & Session Management

### 7. **Authentication & Authorization Flow**

```
User Request
    │
    ├─→ Session Layer
    │       │
    │       ├─→ Split Session Interface
    │       │       ├─→ instructor_session (Admin namespace)
    │       │       └─→ user_session (Learner namespace)
    │       │
    │       └─→ Namespace Validation
    │               ├─→ enforce_namespace_security()
    │               └─→ Route-specific guards
    │
    ├─→ Authentication Middleware
    │       │
    │       ├─→ Flask-Login (load_user)
    │       │       ├─→ Check auth_namespace
    │       │       ├─→ Load from correct table
    │       │       └─→ Verify instance type
    │       │
    │       └─→ Permission Decorators
    │               ├─→ @login_required (Any authenticated)
    │               ├─→ @instructor_required (Admin-only)
    │               ├─→ @teacher_required (Content creators)
    │               └─→ @flexible_login_required (Cross-module)
    │
    ├─→ Route Guards
    │       │
    │       ├─→ before_request handlers
    │       │       ├─→ check_admin_auth()
    │       │       └─→ enforce_namespace_security()
    │       │
    │       └─→ Path Validation
    │               ├─→ /admin/* → Instructor namespace
    │               ├─→ /user/* → Learner namespace
    │               └─→ Cross-check user type
    │
    └─→ Session Security
            │
            ├─→ Namespace Isolation (Prevent poisoning)
            ├─→ CSRF Protection
            ├─→ Session Timeout
            └─→ Activity Tracking
```

---

## Data Flow Summary

### 8. **Complete Request-Response Cycle**

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User/Instructor Browser                      │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    Flask Application    │
                    │    (application.py)     │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Request Processing    │
                    │  - Session validation   │
                    │  - Authentication       │
                    │  - Route matching       │
                    └────────────┬────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
┌─────────▼─────────┐  ┌─────────▼─────────┐  ┌───────▼────────┐
│  Learner Routes   │  │ Instructor Routes │  │  API Endpoints │
│  (user/*)         │  │  (instructor/*)   │  │  (api/*)       │
└─────────┬─────────┘  └─────────┬─────────┘  └───────┬────────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Business Logic Layer  │
                    │  - Controllers          │
                    │  - Services             │
                    │  - Validators           │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    Database Layer       │
                    │  - SQLAlchemy ORM       │
                    │  - MySQL queries        │
                    │  - Transaction mgmt     │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    Response Building    │
                    │  - Template rendering   │
                    │  - JSON serialization   │
                    │  - Error handling       │
                    └────────────┬────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
┌─────────▼─────────┐  ┌─────────▼─────────┐  ┌───────▼────────┐
│   HTML Response   │  │   JSON Response   │  │ WebSocket Event│
│   (Templates)     │  │   (API Data)      │  │   (Real-time)  │
└─────────┬─────────┘  └─────────┬─────────┘  └───────┬────────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Browser Rendering     │
                    │  - UI updates           │
                    │  - User interaction     │
                    │  - State management     │
                    └─────────────────────────┘
```

---

## Key Integration Points

### 9. **Cross-Module Interactions**

```
Instructor → Learner Data Flow:
    ├─→ Content Creation → Content Delivery
    ├─→ Assignment Creation → Task Display
    ├─→ Announcement → Notification
    └─→ Grade Entry → Progress Display

Learner → Instructor Data Flow:
    ├─→ Submission → Review Queue
    ├─→ Progress Update → Analytics
    ├─→ Question Attempt → Score Recording
    └─→ Activity Log → Monitoring Dashboard

Real-time Bidirectional:
    ├─→ WebSocket Events (socket_manager)
    ├─→ Live Progress Updates
    ├─→ Collaboration Locks
    └─→ Chat Messages
```

---

## System Features Summary

### 10. **Feature Modules**

| **Module** | **Learner Features** | **Instructor Features** |
|------------|---------------------|------------------------|
| **Classes** | View enrolled classes, Access modules/lessons | Create/manage classes, Enroll learners |
| **Simulations** | Build topologies, Configure devices, Submit solutions | Design labs, Set validation rules, Review submissions |
| **Assessments** | Take quizzes, Answer questions, View scores | Create question banks, Design rubrics, Grade submissions |
| **Collaboration** | Join team lobbies, Chat with peers, Share workspaces | Monitor team activity, Review collaboration logs |
| **Progress** | View progress dashboard, Track achievements, Earn badges | View analytics, Export reports, Monitor learner activity |
| **Notifications** | Receive alerts, View announcements, Get reminders | Send announcements, Broadcast to classes, Direct messaging |
| **Labs** | Access troubleshooting scenarios, Diagnose problems, Submit solutions | Create scenarios, Configure challenges, Review attempts |

---

## Technology Stack

### 11. **Core Technologies**

```
Backend Framework:
    └─→ Flask (Python web framework)
        ├─→ Flask-Login (Authentication)
        ├─→ Flask-SocketIO (Real-time communication)
        ├─→ Flask-CORS (Cross-origin requests)
        └─→ Flask-Migrate (Database migrations)

Database:
    └─→ MySQL (Relational database)
        └─→ SQLAlchemy ORM (Object-relational mapping)

Real-time:
    └─→ SocketIO (WebSocket protocol)
        └─→ Eventlet (Async I/O)

Frontend:
    └─→ HTML/CSS/JavaScript
        ├─→ Bootstrap (UI framework)
        ├─→ jQuery (DOM manipulation)
        └─→ Socket.IO Client (WebSocket client)

Deployment:
    └─→ AWS Elastic Beanstalk
        ├─→ Gunicorn (WSGI server)
        └─→ Docker (Containerization)
```

---

## Conclusion

This data flow diagram illustrates the comprehensive architecture of the RiddleNet platform, showing how data flows between learners, instructors, and the system components. The dual-module design ensures clear separation of concerns while maintaining seamless integration through shared services and real-time communication channels.

**Key Architectural Principles:**
- **Namespace Isolation**: Separate authentication contexts prevent session poisoning
- **Service Layer**: Business logic isolated from routing for maintainability
- **Real-time Communication**: WebSocket integration for live updates
- **Modular Design**: Clear separation between learner and instructor modules
- **Database Normalization**: Optimized schema for performance and data integrity
- **Security-First**: Multiple authentication layers and route guards

---

**Generated:** October 23, 2025  
**Platform:** RiddleNet Network Simulation & Learning Management System  
**Version:** Production-Ready Architecture
