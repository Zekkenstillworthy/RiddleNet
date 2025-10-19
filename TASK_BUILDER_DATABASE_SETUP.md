# Task Builder Database Setup Guide

## 📋 Overview

The **Task Builder** is an instructor-led task assignment system for RiddleNet that enables:
- Instructors to create structured network configuration tasks
- Students to complete tasks with real-time validation
- Automatic grading based on device placement, configuration, connections, and CLI commands

## 🗄️ Database Requirements

### Tables Required:
1. **`simulations.task_config`** - JSONB column to store task configurations
2. **`task_assignments`** - Table to track student progress and grades

## ✅ Current Status

### Implementation Status:
- ✅ **Backend Model**: `admin/models/task_assignment.py` (fully implemented)
- ✅ **Migration SQL**: `migrations/004_add_task_assignment_system.sql` (ready)
- ✅ **Admin UI**: Task Builder panel in edit_simulation.html (implemented)
- ✅ **Student UI**: Task panel in dynamic_simulation.html (implemented)
- ✅ **API Endpoints**: All admin and student endpoints (implemented)

### Database Status:
- ⚠️ **NEEDS MIGRATION**: Database tables need to be created

## 🚀 Setup Instructions

### Step 1: Add task_config to Simulation Model
The model has been updated with:
```python
# In admin/models/simulation.py
task_config = db.Column(JSON, default=dict)  # Task builder configuration
```

### Step 2: Run the Migration Script

**Option A: Use the Python Migration Script (Recommended)**
```powershell
cd "c:\Users\gilbe\OneDrive\Desktop\RiddleNet - Copy (2)"
python scripts\run_task_builder_migration.py
```

**Option B: Run SQL Directly in PostgreSQL**
```powershell
# Connect to PostgreSQL
psql -U postgres -d riddlenet

# Run the migration
\i migrations/004_add_task_assignment_system.sql
```

### Step 3: Verify Installation
After running the migration, verify:

```sql
-- Check if task_config column exists
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'simulations' AND column_name = 'task_config';

-- Check if task_assignments table exists
SELECT COUNT(*) FROM task_assignments;

-- Check sample data (if simulation id=1 exists)
SELECT id, title, task_config->>'enabled' as task_enabled 
FROM simulations 
WHERE id = 1;
```

## 📊 Database Schema

### simulations.task_config (JSONB)
```json
{
  "enabled": true,
  "device_requirements": [
    {
      "id": "R1",
      "type": "router",
      "model": "Cisco 2911",
      "label": "Router 1",
      "required_config": {
        "hostname": "Router1",
        "interfaces": {...}
      }
    }
  ],
  "connection_requirements": [...],
  "cli_requirements": {...},
  "grading_rubric": {
    "device_placement": 10,
    "device_configuration": 40,
    "connectivity_tests": 30,
    "cli_accuracy": 20
  }
}
```

### task_assignments table
```sql
CREATE TABLE task_assignments (
  id SERIAL PRIMARY KEY,
  simulation_id INTEGER REFERENCES simulations(id),
  user_id INTEGER REFERENCES "user"(id),
  class_id INTEGER REFERENCES class(id),
  
  -- Progress tracking (JSONB)
  devices_placed JSONB DEFAULT '[]',
  devices_configured JSONB DEFAULT '{}',
  connections_made JSONB DEFAULT '[]',
  cli_history JSONB DEFAULT '[]',
  
  -- Grading
  auto_grade_score DECIMAL(5,2) DEFAULT 0.00,
  instructor_grade DECIMAL(5,2),
  feedback TEXT,
  status VARCHAR(20) DEFAULT 'pending',
  
  -- Timestamps
  assigned_at TIMESTAMP,
  started_at TIMESTAMP,
  submitted_at TIMESTAMP,
  graded_at TIMESTAMP,
  
  -- Other fields...
);
```

## 🎯 How to Use After Setup

### For Instructors:

1. **Create a Task Assignment:**
   - Navigate to `/admin/simulation/edit/<id>`
   - Click the clipboard icon (Task Builder) on the right sidebar
   - Toggle "Enable Task Assignment Mode" ON
   - Add devices, connections, and CLI commands
   - Set grading rubric percentages (must total 100%)
   - Click "Save Task Configuration"

2. **View Student Progress:**
   - API: `GET /admin/simulation/api/<simulation_id>/task-assignments`
   - Filter by class or status

3. **Grade Submissions:**
   - API: `POST /admin/simulation/api/task-assignment/<assignment_id>/grade`
   - Body: `{grade: 95, feedback: "Great work!"}`

### For Students:

1. **Complete a Task:**
   - Navigate to `/dynamic/simulation/<id>`
   - Open sidebar → "Task Assignment" tab
   - See requirements and track progress in real-time
   - Complete devices, connections, and CLI commands
   - Click "Submit Task for Grading"

2. **Track Progress:**
   - Progress updates automatically as you work
   - Green checkmarks show completed requirements
   - Progress bar shows overall completion percentage

## 🔧 API Endpoints

### Admin Endpoints:
- `GET /admin/simulation/api/<simulation_id>/task-config` - Get task configuration
- `POST /admin/simulation/api/<simulation_id>/task-config` - Save task configuration
- `GET /admin/simulation/api/<simulation_id>/task-assignments` - Get all assignments
- `GET /admin/simulation/api/task-assignment/<assignment_id>` - Get specific assignment
- `POST /admin/simulation/api/task-assignment/<assignment_id>/grade` - Grade assignment

### Student Endpoints:
- `GET /simulation/api/<simulation_id>/task-config` - Get task requirements
- `GET /simulation/api/<simulation_id>/task-assignment` - Get student's assignment
- `POST /simulation/api/<simulation_id>/validate-progress` - Validate progress
- `POST /simulation/api/<simulation_id>/submit-task` - Submit for grading

## 🐛 Troubleshooting

### Issue: "task_config column does not exist"
**Solution:** Run the migration script (Step 2 above)

### Issue: "task_assignments table does not exist"
**Solution:** Run the migration script (Step 2 above)

### Issue: Task Builder panel doesn't appear
**Solution:** 
1. Clear browser cache
2. Check that simulation model has `task_config` column
3. Restart application: `python run.py`

### Issue: TaskAssignment import error
**Solution:** Make sure migration has been run and restart Python application

## 📁 Files Created/Modified

### Created:
- `admin/models/task_assignment.py` - TaskAssignment model
- `migrations/004_add_task_assignment_system.sql` - Database migration
- `scripts/run_task_builder_migration.py` - Migration runner
- `TASK_BUILDER_DATABASE_SETUP.md` - This file

### Modified:
- `admin/models/simulation.py` - Added `task_config` column
- `admin/routes/simulation_routes.py` - Added API endpoints
- `user/routes/simulation_runner.py` - Added student endpoints
- `templates/admin/troubleshooting/edit_simulation.html` - Added Task Builder UI
- `templates/user/dynamic_simulation.html` - Added Task Panel UI

## 📚 Documentation

For complete implementation details, see:
- `TASK_ASSIGNMENT_IMPLEMENTATION_COMPLETE.md` - Full implementation guide
- `MVP_TASK_ASSIGNMENT_IMPLEMENTATION.md` - MVP specifications

## ✅ Testing Checklist

After setup, verify:
- [ ] Migration script runs without errors
- [ ] `task_config` column exists in simulations table
- [ ] `task_assignments` table exists
- [ ] TaskAssignment model imports successfully
- [ ] Task Builder panel appears in admin editor
- [ ] Task panel appears in student simulation view
- [ ] Can save task configuration
- [ ] Can load existing task configuration
- [ ] Student progress tracks correctly
- [ ] Validation API returns scores
- [ ] Submit task API works

## 🎉 Success!

Once the migration is complete, the Task Builder will be **fully functional**:
- Instructors can create detailed task assignments
- Students can complete tasks with real-time feedback
- Auto-grading calculates scores automatically
- Instructors can review and override grades

---

**Last Updated:** October 19, 2025  
**Version:** 1.0.0  
**Status:** Ready for Migration
