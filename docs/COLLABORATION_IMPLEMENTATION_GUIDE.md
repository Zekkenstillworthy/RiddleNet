# RiddleNet Collaboration Feature Implementation Guide

## Overview
This guide documents the complete implementation of the collaborative troubleshooting feature in RiddleNet, including both the backend infrastructure and frontend user interface components.

## System Architecture

### Backend Components

#### 1. Troubleshooting Lobbies Service (`services/troubleshooting_lobbies.py`)
- **Purpose**: Manages collaborative troubleshooting sessions
- **Key Classes**:
  - `TroubleshootingLobby`: Individual session management
  - `LobbyManager`: Global lobby coordination
  - `CollaborativeSession`: Real-time state synchronization

#### 2. Socket Event Handlers (`socket_events.py`)
- **Purpose**: WebSocket event management for real-time features
- **Key Features**:
  - User authentication and session management
  - Real-time cursor tracking
  - Network diagram synchronization
  - Chat messaging system
  - Lobby join/leave handling

#### 3. Socket Manager (`socket_manager.py`)
- **Purpose**: WebSocket connection management and monitoring
- **Key Features**:
  - Connection lifecycle management
  - User session tracking
  - Connection health monitoring

### Frontend Components

#### 1. Main Template (`templates/user/troubleshoot.html`)
- **Collaboration UI Elements**:
  - Lobby browser modal for session discovery
  - Create lobby modal for session creation
  - Collaboration panel for real-time interaction
  - Connection status indicator

#### 2. Socket Client (`static/js/socket-client.js`)
- **Purpose**: WebSocket client implementation
- **Key Features**:
  - Real-time communication with backend
  - Event handling and dispatching
  - Error handling and reconnection logic

## Implementation Details

### 1. Collaboration Button Integration

The collaboration button is implemented with the following structure:

```html
<div class="action-btn" id="collaborative-session-btn" onclick="showLobbyBrowser()">
    <i class='bx bx-group'></i>
    <span class="label">Collaborate</span>
</div>
```

**Key Functions**:
- `showLobbyBrowser()`: Opens the lobby browser modal
- `closeLobbyBrowser()`: Closes the browser modal
- `refreshLobbies()`: Fetches updated lobby list
- `showCreateLobby()`: Opens the create lobby modal

### 2. Modal System

#### Lobby Browser Modal
- Displays available collaborative sessions
- Shows session metadata (participants, difficulty, scenario)
- Provides join functionality
- Includes refresh and create buttons

#### Create Lobby Modal
- Session name input
- Difficulty level selection
- Scenario type selection
- Maximum participants setting
- Private session option with password

### 3. Real-Time Features

#### Cursor Tracking
- Live mouse position synchronization
- User identification with colored cursors
- Smooth cursor movement animations

#### Network Diagram Sync
- Device placement synchronization
- Connection state sharing
- Real-time network topology updates

#### Chat System
- Instant messaging between participants
- User identification and timestamps
- Message history preservation

### 4. Session Management

#### Lobby Creation
```javascript
function createLobby(formData) {
    const lobby = {
        name: formData.name,
        scenario_type: formData.scenario_type,
        scenario_id: formData.scenario_id,
        max_participants: formData.max_participants,
        is_private: formData.is_private,
        password: formData.password
    };
    
    socketClient.createLobby(lobby);
}
```

#### Joining Sessions
- Automatic lobby discovery
- Password validation for private sessions
- Real-time participant updates
- Session state synchronization

## Technical Specifications

### WebSocket Events

#### Client to Server Events
- `join_lobby`: Join an existing session
- `leave_lobby`: Leave current session
- `create_lobby`: Create new session
- `cursor_move`: Update cursor position
- `network_update`: Sync network changes
- `chat_message`: Send chat message

#### Server to Client Events
- `lobby_joined`: Successful session join
- `lobby_left`: Session leave confirmation
- `lobby_created`: New session confirmation
- `user_cursor`: Other users' cursor positions
- `network_sync`: Network state updates
- `chat_broadcast`: Chat message distribution
- `lobby_list_update`: Available sessions update

### API Endpoints

#### Collaborative Troubleshooting API (`/api/troubleshooting/collaborative/`)
- `GET /lobbies`: List public lobbies
- `POST /lobby`: Create new lobby
- `GET /lobby/<lobby_id>`: Get lobby details
- `POST /lobby/<lobby_id>/join`: Join specific lobby
- `POST /lobby/leave`: Leave current lobby
- `GET /my-lobby`: Get current user's lobby
- `GET /stats`: Get collaboration statistics

### Database Schema

#### Lobbies Table
```sql
CREATE TABLE lobbies (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    creator_id INTEGER NOT NULL,
    scenario_type VARCHAR(50) NOT NULL,
    scenario_id INTEGER,
    max_participants INTEGER DEFAULT 6,
    is_private BOOLEAN DEFAULT FALSE,
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);
```

#### Participants Table
```sql
CREATE TABLE lobby_participants (
    lobby_id VARCHAR(36),
    user_id INTEGER,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(20) DEFAULT 'participant',
    PRIMARY KEY (lobby_id, user_id)
);
```

## Configuration

### Environment Variables
- `SOCKETIO_ASYNC_MODE`: Socket.IO async mode (default: threading)
- `SOCKETIO_CORS_ALLOWED_ORIGINS`: CORS origins for WebSocket
- `COLLABORATION_MAX_LOBBIES`: Maximum concurrent lobbies (default: 100)
- `COLLABORATION_SESSION_TIMEOUT`: Session timeout in minutes (default: 60)

### Flask-SocketIO Configuration
```python
socketio = SocketIO(
    app,
    async_mode='threading',
    cors_allowed_origins="*",
    ping_timeout=60,
    ping_interval=25
)
```

## Testing and Validation

### Backend Testing
The collaboration system has been thoroughly tested with:
- Unit tests for lobby management
- Integration tests for WebSocket events
- Load testing for concurrent sessions
- Error handling validation

### Frontend Testing
- Browser compatibility testing
- Mobile responsiveness validation
- Real-time synchronization accuracy
- Error state handling

## Performance Considerations

### Scalability
- Session-based user management
- Efficient WebSocket connection pooling
- Optimized real-time event handling
- Database query optimization

### Memory Management
- Automatic cleanup of inactive lobbies
- Connection state monitoring
- Garbage collection of disconnected users

### Network Optimization
- Event debouncing for cursor movements
- Batched network state updates
- Compressed message payloads

## Security Features

### Authentication
- User session validation
- WebSocket connection authentication
- Lobby access control

### Data Protection
- Password hashing for private lobbies
- Input validation and sanitization
- XSS prevention in chat messages

### Rate Limiting
- Message frequency limits
- Lobby creation throttling
- Connection attempt limits

## Troubleshooting

### Common Issues

#### Connection Problems
- **Issue**: WebSocket connection fails
- **Solution**: Check CORS settings and firewall configuration
- **Debug**: Enable Socket.IO debugging with `socketio.set_log_level('debug')`

#### Function Scope Errors
- **Issue**: `showLobbyBrowser is not defined`
- **Solution**: Ensure functions are in global scope, not nested in event handlers
- **Fix**: Move function declarations outside DOMContentLoaded event

#### Duplicate DOM Elements
- **Issue**: "Found elements with non-unique id" warnings
- **Solution**: Remove duplicate modal definitions in HTML
- **Prevention**: Use unique IDs for all DOM elements

### Debug Commands
```javascript
// Enable WebSocket debugging
localStorage.debug = 'socket.io-client:socket';

// Check collaboration status
console.log(socketClient.isConnected());

// List active lobbies
socketClient.getPublicLobbies();
```

## Future Enhancements

### Planned Features
1. **Voice Chat Integration**: WebRTC voice communication
2. **Screen Sharing**: Real-time screen sharing capabilities
3. **Advanced Permissions**: Granular user role management
4. **Session Recording**: Collaboration session replay
5. **AI Assistant**: Intelligent troubleshooting suggestions

### Performance Improvements
1. **WebSocket Clustering**: Multi-server WebSocket support
2. **Redis Integration**: Distributed session management
3. **CDN Integration**: Global content delivery
4. **Caching Layer**: Enhanced response times

## Conclusion

The RiddleNet collaboration feature provides a robust, real-time collaborative troubleshooting environment with comprehensive backend infrastructure and intuitive frontend interface. The system is designed for scalability, security, and optimal user experience.

For technical support or feature requests, please refer to the main project documentation or contact the development team.
