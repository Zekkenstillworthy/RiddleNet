# RiddleNet Game Project Design

Date: 2025-10-22
Owner: Zekkenstillworthy
Repository: RiddleNet (main)

RiddleNet is a web-based, gamified learning platform focused on networking fundamentals. It blends time-boxed quiz challenges with interactive simulations and instructor-led content. This document provides a complete design across pre-production, production, and post-production phases, aligned with the current codebase (Flask + Jinja templates, Socket.IO, SQLAlchemy, Docker, AWS EB).

## Pre-Production Phase

### Management
- Stakeholders: Product Owner, Game Designer, Lead Engineer, UI/UX, Content Authors (instructors), QA Lead, DevOps/Release.
- Project roles
  - Product Owner: defines scope and prioritization.
  - Game Designer: gameplay loops, difficulty curves, rewards.
  - Lead Engineer: architecture, code quality gates, security.
  - UI/UX: responsive layouts, accessibility, visual identity.
  - Content Authors: quiz banks, simulation tasks, hints, explanations.
  - QA Lead: test plans, automation, release sign-off.
  - DevOps: containerization, CI/CD, monitoring, rollbacks.
- Collaboration: GitHub Issues/Projects, PR reviews, design docs in repo, weekly milestone review.
- Environments: local dev, staging (Docker Compose), production (AWS Elastic Beanstalk).

### Requirements Specification
- Functional requirements
  - Authentication and role separation (user vs instructor/admin) with strict namespace isolation.
  - Quiz Challenges with timed questions, lifelines (50/50, skip, hint), explanations, scoring, and progress tracking.
  - Dynamic networking simulations (topology building, device palette, troubleshooting scenarios) with persistence.
  - Instructor/Admin portal for content authoring, class management, analytics, and audits.
  - Notifications and assignment workflows.
  - Mobile-first responsive UI for quizzes and simulations.
- Non-functional requirements
  - Performance: fast TTFB, lightweight client, efficient DB queries.
  - Security: session isolation, CSRF protection, auth namespace validation, audit logs.
  - Availability: health endpoint (/health), graceful error handling, logging.
  - Usability & Accessibility: keyboard/touch support, contrast and motion preferences, orientation aides.
  - Portability: Dockerized dev/test, Linux-friendly for production, Windows-friendly for developers.
- Data model highlights (conceptual)
  - User, Instructor, Class, Assignment, QuizQuestion, QuizAttempt, Score, Notification, TopologyProgress.
  - Relationships: Instructors manage Classes; Users submit Assignments and Attempts; Scores summarized per user/class.

### Game Design Document (GDD)
- Game overview
  - Core loop: Learn → Attempt quiz or scenario → Receive feedback and hints → Progress → Unlock harder challenges.
  - Modes: Quiz Challenge (timed MCQ); Troubleshooting; Topology Build (drag-and-drop devices), Instructor Labs.
  - Progression: escalating difficulty, streak multipliers, badges/achievements (MVP: score + completion).
- Art style
  - Cyber/tech aesthetic with neon accents, glassmorphism, Orbitron-like monospaced display typography.
  - Motion: subtle, performant transitions; reduced-motion respect.
- User interface
  - Quiz HUD: time remaining, progress, score, lifelines; mobile-optimized, landscape helpers.
  - Results: accuracy, time bonus, per-question feedback and explanations.
  - Simulations: device palette, canvas, contextual panels; responsive layout.
- Controls
  - Desktop: mouse + keyboard shortcuts where applicable.
  - Mobile/Tablet: touch-first, large hit targets, orientation helpers.
- Platforms
  - Web (Chrome, Edge, Safari, Firefox), Desktop and Mobile.
  - Backend: Flask (WSGI) with Socket.IO for real-time features.
- Target audience
  - Students learning networking basics; educators managing classes; self-learners preparing for exams.

### Game Prototyping
- Quiz prototype
  - Template: `templates/user/quiz_challenge.html` with stats, timer, lifelines, options, hints.
  - API: user quiz routes and blueprint (`user.routes.quiz_routes`), client-side state and progress bar.
  - Content: seed with ~15 curated questions (network types, devices, OSI).
- Simulation prototype
  - Topology routes and device palette as an interactive canvas (admin + user flows).
  - Minimal viable tasks: connect devices, verify pings, identify misconfigurations.
- Success metrics
  - Time to first correct answer (<30s), quiz completion rates, hint usage rates, mobile completion parity.

## Production Phase

### Asset Creation
- Visual: CSS variables and themes, neon gradients, icons (Font Awesome), device images under `static/img`.
- Audio (optional): minimal UI feedback (select, correct/wrong) with user-toggle.
- Fonts: display font for titles, system or web-safe for body; ensure licensing.
- Deliverables live under `/static/css`, `/static/js`, `/static/img`.

### Storyboard Production
1) Landing/Overview → 2) Select Challenge → 3) Quiz HUD with timer → 4) Answer + lifeline → 5) Feedback → 6) Next question → 7) Results summary → 8) Recommendations/Next challenge.
- Troubleshooting storyboard: receive faulty topology → inspect logs/links → make changes → run verification → score + feedback.

### Development
- Architecture
  - Backend: Flask app (`application.py` entry for AWS EB), blueprints for user and instructor areas, SQLAlchemy ORM, CORS for specific admin endpoints.
  - Real-time: Socket.IO init via `socket_manager`.
  - Frontend: Jinja templates + modular JS; responsive CSS with orientation utilities.
  - Persistence: relational DB (SQLite locally, Postgres in staging/production), migrations and table setup on boot.
- Coding standards
  - Python: PEP8/black-compatible style, type hints where useful, blueprint modularity.
  - JS: small modules, no blocking operations, feature flags for experimental UI.
  - Security: namespace enforcement middleware, minimal session scope, role checks at route boundaries.
- Performance
  - Lazy-load media, trim CSS/JS, cache headers for static assets, DB indexing for hot paths.

### Source Code
- Key files and modules
  - `application.py`: WSGI entry (AWS EB), blueprint registration, security middlewares, health endpoint.
  - `__init__.py`: `create_app` factory and DB initialization.
  - `templates/user/quiz_challenge.html`: primary quiz UI.
  - `instructor.*` and `user.*`: routes, controllers, models, APIs.
  - `Dockerfile`, `docker-compose.yml`, `gunicorn.conf.py`: containerization and production-like serving.
  - `static/*`: CSS/JS/IMG assets (orientation helpers, forces landscape when needed).
- Branching and releases
  - `main` protected; feature branches via PRs; tagged releases with changelog notes.

### Game Engine
- Engine model
  - Server-driven web game using Flask + Socket.IO; event-driven rather than a frame-based loop.
  - Rendering via HTML/CSS; templating via Jinja; interactions in JS.
- Timing and state
  - Client timers drive HUD; authoritative scoring and attempt persistence on server.
  - Lifelines: implemented as client triggers with server-side validation and usage caps.

### Implementation
- Quiz implementation
  - API endpoints: fetch questions, submit answers, use lifelines, persist attempts, return explanations.
  - Client: dynamic question rendering, progress bar, responsive states, hint reveal, result summary.
  - Data: question bank with difficulty tags, correct index, explanations, optional image.
- Simulation implementation
  - Canvas: device components with ports/links; actions emit events; validator checks correctness.
  - Persistence: save/load topology progress (`/dynamic` endpoints and progress APIs).
- Instructor/Admin
  - Auth namespace `admin` with strict checks; content management: questions, classes, assignments.
  - Analytics: attempt accuracy, time-to-answer, hint rate, device errors.

## Post-Production Phase

### Quality Assurance
- Test plans
  - Unit tests: models, utilities, scoring logic, permission checks.
  - Integration tests: quiz flows (fetch → answer → result), admin content CRUD, namespace guardrails.
  - E2E smoke: login → select challenge → complete quiz → view results (desktop + mobile landscape/portrait).
  - Cross-browser: latest Chrome/Edge/Firefox/Safari; mobile Chrome/Safari.
  - Accessibility: keyboard nav, focus states, ARIA where needed, prefers-reduced-motion.
  - Security: session fixation, CSRF, authz bypass attempts, rate-limited lifelines.
- Performance & reliability
  - Health checks: `/health` monitored; error budgets for downtime; log sampling and alerts.

### Testing
- Local: run Flask app, validate quiz UI responsiveness, try lifelines and progress save.
- Staging: Docker Compose with optional Postgres and Redis; test `/health`, load, and session behavior.
- Observability: collect application logs, slow query logs, Socket.IO event errors.

### Release
- Packaging & deploy
  - Container image built from `Dockerfile` using Gunicorn and WSGI entry.
  - AWS Elastic Beanstalk-compatible app (`application` WSGI variable) with `/health` endpoint.
- Versioning & rollout
  - Semantic versioning; release candidates on staging; production with blue/green or rolling updates.
  - Rollback plan: keep last known-good image and EB config; DB migrations are backward-compatible when possible.
- Release criteria
  - All critical tests PASS; no P0/P1 bugs open; performance SLOs met; accessibility checks pass.

---

## Appendices
- Related files in repo
  - `templates/user/quiz_challenge.html` (responsive quiz UI with timers, lifelines, hints)
  - `application.py` (WSGI entry, blueprints, security, `/health`)
  - `Dockerfile`, `docker-compose.yml` (production-like serving via Gunicorn; local staging stack)
- Future enhancements
  - Achievements and leaderboards; question tagging and adaptive difficulty; richer simulation validators; offline-first quiz mode.
