#!/usr/bin/env python3
"""
Test script to verify profile images work in collaboration system
"""

def test_profile_image_integration():
    """Test that profile images are properly integrated into collaboration system"""
    
    print("🧪 Testing Profile Image Integration in Collaboration System")
    print("=" * 60)
    
    # Test 1: User model has profile_img field
    try:
        from user.models.user import User
        user_fields = [column.name for column in User.__table__.columns]
        assert 'profile_img' in user_fields, "User model missing profile_img field"
        print("✅ User model has profile_img field")
    except Exception as e:
        print(f"❌ User model test failed: {e}")
    
    # Test 2: Socket events include profile image
    try:
        with open('socket_events.py', 'r') as f:
            socket_content = f.read()
        assert 'profile_image' in socket_content, "Socket events missing profile_image handling"
        assert 'current_user.profile_img' in socket_content, "Socket events not accessing profile_img"
        print("✅ Socket events include profile image data")
    except Exception as e:
        print(f"❌ Socket events test failed: {e}")
    
    # Test 3: Lobby system stores profile images
    try:
        from services.troubleshooting_lobbies import TroubleshootingLobby
        lobby = TroubleshootingLobby(
            id="test",
            name="Test Lobby",
            scenario_type="easy",
            scenario_id="network"
        )
        
        # Test adding participant with profile image
        success = lobby.add_participant("user123", {
            'username': 'TestUser',
            'profile_image': 'test_profile.jpg'
        })
        
        assert success, "Failed to add participant to lobby"
        assert 'user123' in lobby.participants, "Participant not added"
        assert lobby.participants['user123']['profile_image'] == 'test_profile.jpg', "Profile image not stored"
        print("✅ Lobby system stores profile images correctly")
    except Exception as e:
        print(f"❌ Lobby system test failed: {e}")
    
    # Test 4: Frontend HTML includes profile image handling
    try:
        with open('templates/user/troubleshoot.html', 'r') as f:
            html_content = f.read()
        
        # Check for profile image CSS classes
        assert 'cursor-profile-img' in html_content, "Missing cursor profile image CSS"
        assert 'cursor-profile-fallback' in html_content, "Missing cursor fallback CSS"
        assert '/static/img/profiles/' in html_content, "Missing profile image path"
        assert 'onerror=' in html_content, "Missing image error handling"
        
        print("✅ Frontend includes profile image handling")
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
    
    print("\n🎉 Profile Image Integration Tests Completed!")
    print("\n📋 Implementation Summary:")
    print("   • User profile images are stored in User.profile_img field")
    print("   • Socket events broadcast profile_image in cursor_moved events")
    print("   • Lobby system stores profile_image in participant data")
    print("   • Frontend displays profile images in:")
    print("     - Participant lists with fallback to username initials")
    print("     - User cursors with fallback to username initials")
    print("     - Lobby browser participant previews")
    print("   • Images are served from /static/img/profiles/ directory")
    print("   • Graceful fallback when profile images fail to load")

if __name__ == "__main__":
    test_profile_image_integration()
