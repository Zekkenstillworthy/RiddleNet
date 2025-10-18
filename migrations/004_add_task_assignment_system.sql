-- Migration: Add Task Assignment System
-- Description: Add task_config to simulations and create task_assignments table
-- Date: 2025-10-17

-- Step 1: Add task_config column to simulations table
ALTER TABLE simulations 
ADD COLUMN IF NOT EXISTS task_config JSONB DEFAULT '{
  "enabled": false,
  "device_requirements": [],
  "connection_requirements": [],
  "cli_requirements": {},
  "grading_rubric": {
    "device_placement": 10,
    "device_configuration": 40,
    "connectivity_tests": 30,
    "cli_accuracy": 20
  },
  "task_mode": "combined"
}'::jsonb;

-- Step 2: Create task_assignments table for tracking student progress
CREATE TABLE IF NOT EXISTS task_assignments (
  id SERIAL PRIMARY KEY,
  simulation_id INTEGER NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
  user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  class_id INTEGER REFERENCES class(id) ON DELETE SET NULL,
  
  -- Assignment Metadata
  assigned_at TIMESTAMP DEFAULT NOW(),
  due_date TIMESTAMP,
  
  -- Progress Tracking (JSONB for flexibility)
  devices_placed JSONB DEFAULT '[]'::jsonb,
  devices_configured JSONB DEFAULT '{}'::jsonb,
  connections_made JSONB DEFAULT '[]'::jsonb,
  cli_history JSONB DEFAULT '[]'::jsonb,
  
  -- Grading
  auto_grade_score DECIMAL(5,2) DEFAULT 0.00,
  instructor_grade DECIMAL(5,2),
  feedback TEXT,
  
  -- Status Management
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'submitted', 'graded', 'returned')),
  
  -- Timestamps
  started_at TIMESTAMP,
  submitted_at TIMESTAMP,
  graded_at TIMESTAMP,
  returned_at TIMESTAMP,
  
  -- Validation Results (store last validation)
  validation_results JSONB DEFAULT '{}'::jsonb,
  
  -- Attempt Tracking
  attempt_count INTEGER DEFAULT 0,
  last_activity_at TIMESTAMP DEFAULT NOW(),
  
  -- Unique constraint to prevent duplicate assignments
  UNIQUE(simulation_id, user_id, class_id),
  
  -- Indexes for performance
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_task_assignments_user_id ON task_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_task_assignments_simulation_id ON task_assignments(simulation_id);
CREATE INDEX IF NOT EXISTS idx_task_assignments_class_id ON task_assignments(class_id);
CREATE INDEX IF NOT EXISTS idx_task_assignments_status ON task_assignments(status);
CREATE INDEX IF NOT EXISTS idx_task_assignments_due_date ON task_assignments(due_date);

-- Step 3: Create function to update last_activity_at automatically
CREATE OR REPLACE FUNCTION update_task_assignment_activity()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_activity_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic activity timestamp updates
DROP TRIGGER IF EXISTS trigger_update_task_assignment_activity ON task_assignments;
CREATE TRIGGER trigger_update_task_assignment_activity
    BEFORE UPDATE ON task_assignments
    FOR EACH ROW
    EXECUTE FUNCTION update_task_assignment_activity();

-- Step 4: Add sample task configuration to an existing simulation (optional)
-- Update simulation with id=1 to have a sample task config
UPDATE simulations 
SET task_config = '{
  "enabled": true,
  "device_requirements": [
    {
      "id": "R1",
      "type": "router",
      "model": "Cisco 2911",
      "label": "Router 1",
      "required_config": {
        "hostname": "Router1",
        "interfaces": {
          "GigabitEthernet0/0": {
            "ip": "192.168.1.1",
            "subnet": "255.255.255.0",
            "description": "LAN Interface"
          }
        }
      }
    },
    {
      "id": "SW1",
      "type": "switch",
      "model": "Cisco 2960",
      "label": "Switch 1",
      "required_config": {
        "hostname": "Switch1",
        "vlans": [10, 20]
      }
    },
    {
      "id": "PC1",
      "type": "pc",
      "model": "Desktop",
      "label": "PC 1",
      "required_config": {
        "ip": "192.168.1.10",
        "gateway": "192.168.1.1"
      }
    }
  ],
  "connection_requirements": [
    {
      "source_device": "R1",
      "source_interface": "GigabitEthernet0/0",
      "target_device": "SW1",
      "target_interface": "FastEthernet0/1",
      "cable_type": "straight-through"
    },
    {
      "source_device": "SW1",
      "source_interface": "FastEthernet0/2",
      "target_device": "PC1",
      "target_interface": "Ethernet0",
      "cable_type": "straight-through"
    }
  ],
  "cli_requirements": {
    "R1": [
      {
        "command": "configure terminal",
        "order": 1,
        "required": true,
        "validation": "exact_match"
      },
      {
        "command": "hostname Router1",
        "order": 2,
        "required": true,
        "validation": "exact_match"
      },
      {
        "command": "interface GigabitEthernet0/0",
        "order": 3,
        "required": true,
        "validation": "exact_match"
      },
      {
        "command": "ip address 192.168.1.1 255.255.255.0",
        "order": 4,
        "required": true,
        "validation": "ip_format"
      },
      {
        "command": "no shutdown",
        "order": 5,
        "required": true,
        "validation": "exact_match"
      }
    ],
    "SW1": [
      {
        "command": "configure terminal",
        "order": 1,
        "required": true,
        "validation": "exact_match"
      },
      {
        "command": "hostname Switch1",
        "order": 2,
        "required": true,
        "validation": "exact_match"
      }
    ]
  },
  "grading_rubric": {
    "device_placement": 10,
    "device_configuration": 40,
    "connectivity_tests": 30,
    "cli_accuracy": 20
  },
  "task_mode": "combined",
  "instructions": "Configure a basic network with one router, one switch, and one PC. Complete all device configurations and establish proper connectivity.",
  "time_limit_minutes": 45
}'::jsonb
WHERE id = 1 AND EXISTS (SELECT 1 FROM simulations WHERE id = 1);

-- Verification queries (commented out, run separately if needed)
-- SELECT id, title, task_config->>'enabled' as task_enabled FROM simulations WHERE task_config->>'enabled' = 'true';
-- SELECT * FROM task_assignments;
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'task_assignments';

COMMENT ON TABLE task_assignments IS 'Tracks student progress on instructor-assigned network configuration tasks';
COMMENT ON COLUMN task_assignments.task_config IS 'JSONB field storing task requirements, grading criteria, and instructions';
