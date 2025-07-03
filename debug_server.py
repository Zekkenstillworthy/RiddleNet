"""
Simple test server to debug chat display issues
"""
from flask import Flask, render_template, request, jsonify, session
from services.troubleshooting_lobbies import lobby_manager
import json

app = Flask(__name__)
app.secret_key = 'debug-secret-key'

@app.route('/')
def index():
    return render_template('user/troubleshoot.html')

@app.route('/test-chat')
def test_chat():
    """Test endpoint to create a lobby with chat messages"""
    # Create a test lobby
    lobby = lobby_manager.create_lobby(
        creator_id='debug_user',
        creator_name='Debug User',
        lobby_config={
            'name': 'Debug Chat Test',
            'scenario_type': 'easy',
            'scenario_id': 'network'
        },
        creator_profile_image='test_avatar.jpg'
    )
    
    # Add test messages
    lobby.add_chat_message('debug_user', 'Hello from debug user!', 'text')
    lobby.add_chat_message('system', 'This is a system message', 'system')
    
    return jsonify({
        'lobby_id': lobby.id,
        'lobby_data': lobby.to_dict(),
        'chat_count': len(lobby.chat_history),
        'recent_chat': lobby.to_dict().get('recent_chat', [])
    })

@app.route('/api/lobby/<lobby_id>')
def get_lobby(lobby_id):
    """Get lobby data"""
    lobby = lobby_manager.get_lobby_by_id(lobby_id)
    if not lobby:
        return jsonify({'error': 'Lobby not found'}), 404
    
    return jsonify(lobby.to_dict())

if __name__ == '__main__':
    app.run(debug=True, port=5001)
