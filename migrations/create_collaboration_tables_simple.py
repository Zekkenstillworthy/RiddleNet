#!/usr/bin/env python3
"""
Simple migration script to create collaboration tables using psycopg2
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def create_collaboration_tables():
    """Create collaboration_settings, collaboration_lobbies, and team_assignments tables using psycopg2"""
    try:
        # Get database connection details from environment
        db_url = f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'admin')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'RiddleNet')}"
        
        # Connect to database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Create collaboration_settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collaboration_settings (
                id SERIAL PRIMARY KEY,
                simulation_id INTEGER REFERENCES simulations(id),
                class_id INTEGER REFERENCES classes(id),
                collaboration_enabled BOOLEAN DEFAULT FALSE,
                team_size INTEGER DEFAULT 2,
                shared_terminal BOOLEAN DEFAULT FALSE,
                individual_terminals BOOLEAN DEFAULT TRUE,
                follow_leader BOOLEAN DEFAULT FALSE,
                chat_enabled BOOLEAN DEFAULT FALSE,
                transcript_logging BOOLEAN DEFAULT FALSE,
                allow_late_join BOOLEAN DEFAULT TRUE,
                require_instructor BOOLEAN DEFAULT FALSE,
                time_window INTEGER,
                roles JSON DEFAULT '["Leader", "Observer", "Operator"]',
                created_by INTEGER REFERENCES admin(id) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create collaboration_lobbies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collaboration_lobbies (
                id VARCHAR(8) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                scenario_type VARCHAR(50) DEFAULT 'medium',
                scenario_id VARCHAR(100) DEFAULT 'network',
                max_participants INTEGER DEFAULT 6,
                class_id INTEGER REFERENCES classes(id),
                simulation_id INTEGER REFERENCES simulations(id),
                creator_id VARCHAR(50) NOT NULL,
                creator_name VARCHAR(255) NOT NULL,
                creator_profile_image TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                is_locked BOOLEAN DEFAULT FALSE,
                participants JSON DEFAULT '{}',
                network_state JSON DEFAULT '{}',
                device_locks JSON DEFAULT '{}',
                cli_history JSON DEFAULT '{}',
                progress JSON DEFAULT '{}',
                chat_history JSON DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create team_assignments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_assignments (
                id SERIAL PRIMARY KEY,
                class_id INTEGER REFERENCES classes(id) NOT NULL,
                simulation_id INTEGER REFERENCES simulations(id),
                lobby_id VARCHAR(8) REFERENCES collaboration_lobbies(id),
                team_name VARCHAR(255) NOT NULL,
                team_members JSON NOT NULL,
                team_leader VARCHAR(50),
                created_by INTEGER REFERENCES admin(id) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            );
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_collaboration_settings_simulation 
            ON collaboration_settings(simulation_id);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_collaboration_settings_class 
            ON collaboration_settings(class_id);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_collaboration_lobbies_simulation 
            ON collaboration_lobbies(simulation_id);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_collaboration_lobbies_class 
            ON collaboration_lobbies(class_id);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_team_assignments_class 
            ON team_assignments(class_id);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_team_assignments_simulation 
            ON team_assignments(simulation_id);
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("[OK] Successfully created collaboration tables")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error creating collaboration tables: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_collaboration_tables()
    exit(0 if success else 1)