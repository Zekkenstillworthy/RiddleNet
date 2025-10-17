"""
Lobby Migration Script
=====================
Migrates existing in-memory lobbies to PostgreSQL database.

Usage:
    python migrate_lobbies_to_db.py [--test]

Options:
    --test    Run in test mode (dry-run, no database writes)

This script:
1. Loads active lobbies from the LobbyManager
2. Saves each lobby and its participants to the database
3. Verifies the migration was successful
4. Provides a summary report
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from application import create_app
from services.troubleshooting_lobbies import lobby_manager
from services.lobby_persistence import lobby_persistence
from user.models.collaboration_lobby import (
    CollaborationLobby, LobbyParticipant, 
    LobbyChatMessage, LobbyDeviceLock, LobbyCLIHistory
)


class LobbyMigrator:
    """Handles migration of in-memory lobbies to database."""
    
    def __init__(self, test_mode=False):
        self.test_mode = test_mode
        self.stats = {
            'total_lobbies': 0,
            'migrated_lobbies': 0,
            'failed_lobbies': 0,
            'total_participants': 0,
            'total_messages': 0,
            'total_locks': 0,
            'total_cli_commands': 0,
            'errors': []
        }
    
    def migrate_all_lobbies(self):
        """Migrate all active lobbies from memory to database."""
        print("🔄 Starting lobby migration...")
        print(f"   Mode: {'TEST (dry-run)' if self.test_mode else 'PRODUCTION'}")
        print()
        
        # Get all active lobbies from memory
        with lobby_manager._lock:
            active_lobbies = list(lobby_manager._lobbies.values())
        
        self.stats['total_lobbies'] = len(active_lobbies)
        
        if not active_lobbies:
            print("ℹ️  No active lobbies found in memory")
            return
        
        print(f"📊 Found {len(active_lobbies)} active lobbies to migrate\n")
        
        # Migrate each lobby
        for idx, lobby in enumerate(active_lobbies, 1):
            print(f"[{idx}/{len(active_lobbies)}] Migrating lobby '{lobby.name}' (ID: {lobby.lobby_id})...")
            
            try:
                self._migrate_single_lobby(lobby)
                self.stats['migrated_lobbies'] += 1
                print(f"   ✅ Success\n")
            except Exception as e:
                self.stats['failed_lobbies'] += 1
                error_msg = f"Lobby {lobby.lobby_id}: {str(e)}"
                self.stats['errors'].append(error_msg)
                print(f"   ❌ Failed: {str(e)}\n")
        
        self._print_summary()
    
    def _migrate_single_lobby(self, lobby):
        """Migrate a single lobby and all its associated data."""
        if self.test_mode:
            print("   [TEST MODE] Skipping database write")
            self._simulate_migration(lobby)
            return
        
        # 1. Migrate lobby itself
        print("   - Saving lobby data...", end=" ")
        lobby_persistence.save_lobby(lobby)
        print("✓")
        
        # 2. Migrate participants
        print(f"   - Saving {len(lobby.participants)} participants...", end=" ")
        for user_id, participant in lobby.participants.items():
            lobby_persistence.save_participant(lobby.lobby_id, user_id, participant)
            self.stats['total_participants'] += 1
        print("✓")
        
        # 3. Migrate chat messages
        if lobby.chat_messages:
            print(f"   - Saving {len(lobby.chat_messages)} chat messages...", end=" ")
            for message in lobby.chat_messages:
                lobby_persistence.save_chat_message(lobby.lobby_id, message)
                self.stats['total_messages'] += 1
            print("✓")
        
        # 4. Migrate device locks
        if lobby.device_locks:
            print(f"   - Saving {len(lobby.device_locks)} device locks...", end=" ")
            for device_id, lock_info in lobby.device_locks.items():
                lobby_persistence.save_device_lock(lobby.lobby_id, device_id, lock_info)
                self.stats['total_locks'] += 1
            print("✓")
        
        # 5. Migrate CLI history
        if lobby.cli_history:
            total_commands = sum(len(commands) for commands in lobby.cli_history.values())
            if total_commands > 0:
                print(f"   - Saving {total_commands} CLI commands...", end=" ")
                for device_id, commands in lobby.cli_history.items():
                    for command_data in commands:
                        lobby_persistence.save_cli_command(lobby.lobby_id, device_id, command_data)
                        self.stats['total_cli_commands'] += 1
                print("✓")
    
    def _simulate_migration(self, lobby):
        """Simulate migration in test mode."""
        self.stats['total_participants'] += len(lobby.participants)
        self.stats['total_messages'] += len(lobby.chat_messages)
        self.stats['total_locks'] += len(lobby.device_locks)
        for commands in lobby.cli_history.values():
            self.stats['total_cli_commands'] += len(commands)
    
    def _print_summary(self):
        """Print migration summary report."""
        print("\n" + "="*60)
        print("📊 MIGRATION SUMMARY")
        print("="*60)
        print(f"Mode:                    {'TEST (dry-run)' if self.test_mode else 'PRODUCTION'}")
        print(f"Total Lobbies Found:     {self.stats['total_lobbies']}")
        print(f"Successfully Migrated:   {self.stats['migrated_lobbies']}")
        print(f"Failed:                  {self.stats['failed_lobbies']}")
        print()
        print(f"Total Participants:      {self.stats['total_participants']}")
        print(f"Total Chat Messages:     {self.stats['total_messages']}")
        print(f"Total Device Locks:      {self.stats['total_locks']}")
        print(f"Total CLI Commands:      {self.stats['total_cli_commands']}")
        print("="*60)
        
        if self.stats['errors']:
            print("\n❌ ERRORS:")
            for error in self.stats['errors']:
                print(f"   - {error}")
        
        if self.stats['migrated_lobbies'] > 0 and not self.test_mode:
            print("\n✅ Migration completed successfully!")
            print("   All lobbies have been saved to the database.")
        elif self.test_mode:
            print("\n✅ Test run completed successfully!")
            print("   No data was written to the database.")
    
    def verify_migration(self):
        """Verify that migrated lobbies exist in database."""
        if self.test_mode:
            print("\nℹ️  Skipping verification in test mode")
            return
        
        print("\n🔍 Verifying migration...")
        
        try:
            db_lobbies = lobby_persistence.get_all_active_lobbies()
            print(f"✅ Found {len(db_lobbies)} active lobbies in database")
            
            for lobby in db_lobbies:
                print(f"   - {lobby['name']} (ID: {lobby['lobby_id']}) - {len(lobby['participants'])} participants")
        
        except Exception as e:
            print(f"❌ Verification failed: {str(e)}")


def main():
    """Main migration entry point."""
    # Check for test mode flag
    test_mode = '--test' in sys.argv or '-t' in sys.argv
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Create migrator instance
        migrator = LobbyMigrator(test_mode=test_mode)
        
        # Run migration
        migrator.migrate_all_lobbies()
        
        # Verify migration (production mode only)
        if not test_mode and migrator.stats['migrated_lobbies'] > 0:
            migrator.verify_migration()
        
        print("\n" + "="*60)
        print("🎉 Migration script completed")
        print("="*60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Migration failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
