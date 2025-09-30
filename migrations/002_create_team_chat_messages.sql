-- MVP Team Chat Messages Table Migration
-- Creates the team_chat_messages table for persistent team chat functionality

CREATE TABLE IF NOT EXISTS team_chat_messages (
    id BIGSERIAL PRIMARY KEY,
    simulation_session_id BIGINT NOT NULL,
    team_id BIGINT NULL,
    lobby_id BIGINT NULL,
    user_id BIGINT NOT NULL,
    username_cache VARCHAR(150),
    content TEXT NOT NULL CHECK (LENGTH(content) >= 1 AND LENGTH(content) <= 2000),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE NULL
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_tcm_session_team_created 
    ON team_chat_messages (simulation_session_id, team_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_tcm_session_lobby_created 
    ON team_chat_messages (simulation_session_id, lobby_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_tcm_user_created 
    ON team_chat_messages (user_id, created_at);

-- Optional: Foreign key constraints (adjust based on your existing schema)
-- ALTER TABLE team_chat_messages ADD CONSTRAINT fk_tcm_user_id 
--     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Add comment for documentation
COMMENT ON TABLE team_chat_messages IS 'Stores team chat messages for real-time collaboration sessions';
COMMENT ON COLUMN team_chat_messages.simulation_session_id IS 'ID of the simulation session';
COMMENT ON COLUMN team_chat_messages.team_id IS 'Team ID within the session (nullable for lobby-based chat)';
COMMENT ON COLUMN team_chat_messages.lobby_id IS 'Lobby ID for collaboration mode (nullable for team-based chat)';
COMMENT ON COLUMN team_chat_messages.user_id IS 'ID of the user who sent the message';
COMMENT ON COLUMN team_chat_messages.username_cache IS 'Cached username for faster retrieval';
COMMENT ON COLUMN team_chat_messages.content IS 'Message content (1-2000 characters)';
COMMENT ON COLUMN team_chat_messages.created_at IS 'When the message was sent';
COMMENT ON COLUMN team_chat_messages.deleted_at IS 'Soft delete timestamp (future use)';