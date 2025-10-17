"""
Database migration script to create collaboration lobby tables
Run this script to add the new tables to your PostgreSQL database

Usage:
    python create_lobby_tables.py
"""

from __init__ import create_app, db
from user.models.collaboration_lobby import (
    CollaborationLobby, LobbyParticipant, LobbyChatMessage,
    LobbyDeviceLock, LobbyCLIHistory
)

def create_lobby_tables():
    """Create all lobby-related tables"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 Creating collaboration lobby tables...")
            
            # Create all tables defined in the models
            db.create_all()
            
            print("✅ Successfully created lobby tables:")
            print("   - collaboration_lobby")
            print("   - lobby_participant")
            print("   - lobby_chat_message")
            print("   - lobby_device_lock")
            print("   - lobby_cli_history")
            print("\n🎉 Database migration complete!")
            print("\n📝 Tables are ready to store:")
            print("   • Collaboration lobbies/sessions")
            print("   • Participant information and cursor positions")
            print("   • Team chat history")
            print("   • Device locks for exclusive editing")
            print("   • CLI command history")
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            raise

if __name__ == '__main__':
    create_lobby_tables()
