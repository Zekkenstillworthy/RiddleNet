# 🚀 Real-Time Collaborative Troubleshooting System

## Overview

This system transforms RiddleNet's troubleshooting into a collaborative, real-time experience similar to Figma and Canva. Multiple users can work together on network troubleshooting scenarios, seeing each other's cursors, sharing network topology changes, and communicating through integrated chat.

## 🌟 Key Features

### **Figma-like Collaboration**
- **Real-time Cursor Tracking**: See other users' mouse cursors in real-time
- **Live Network Topology**: All participants see the same network state
- **Instant Synchronization**: Changes are immediately visible to all participants
- **Visual User Indicators**: Color-coded participants with unique avatars

### **Canva-style Session Management**
- **Easy Lobby Creation**: Create sessions with custom settings
- **Session Discovery**: Browse and join available public sessions
- **Private Sessions**: Password-protected collaborative sessions
- **Flexible Scenarios**: Support for all difficulty levels and scenario types

### **Advanced Team Features**
- **Real-time Chat**: Built-in messaging system for team communication
- **Progress Sharing**: Team progress tracking and individual contributions
- **Device Selection**: See what network devices teammates are working on
- **History Tracking**: Complete audit trail of all network changes

## 📁 File Structure

```
RiddleNet/
├── services/
│   └── troubleshooting_lobbies.py          # Core lobby management system
├── socket_events.py                         # WebSocket event handlers
├── user/routes/
│   ├── troubleshooting_routes.py           # Main troubleshooting routes
│   └── collaborative_troubleshooting_api.py # Collaborative API endpoints
├── templates/user/
│   └── troubleshoot.html                   # Frontend with collaborative UI
├── static/js/
│   └── socket-client.js                    # WebSocket client integration
└── test_collaborative_troubleshooting.py   # Test suite
```

## 🔧 Technical Architecture

### **Backend Components**

#### 1. Lobby Management (`services/troubleshooting_lobbies.py`)
- **TroubleshootingLobby**: Data class representing a collaborative session
- **LobbyManager**: Manages all active sessions with thread safety
- **Features**: Participant management, network state synchronization, chat history

#### 2. WebSocket Events (`socket_events.py`)
- **Lobby Management**: Create, join, leave sessions
- **Real-time Collaboration**: Cursor updates, network changes, chat messages
- **Admin Controls**: Administrative lobby management

#### 3. API Endpoints (`user/routes/collaborative_troubleshooting_api.py`)
- REST API for lobby operations
- Integration with existing troubleshooting system
- Statistics and monitoring endpoints

### **Frontend Components**

#### 1. Collaborative UI (`templates/user/troubleshoot.html`)
- **Lobby Browser Modal**: Discover and join sessions
- **Create Session Modal**: Set up new collaborative sessions
- **Collaboration Panel**: Live participants list and chat
- **User Cursors**: Real-time cursor visualization

#### 2. JavaScript Integration
- WebSocket event handling
- Real-time UI updates
- Mouse tracking and cursor sharing
- Network topology synchronization

## 🚀 Quick Start

### 1. **Start a Collaborative Session**
```javascript
// Create a new session
const lobbyConfig = {
    name: "Team Network Lab",
    scenario_type: "medium",
    scenario_id: "split",
    max_participants: 6,
    is_private: false
};

window.socketClient.createTroubleshootingLobby(lobbyConfig);
```

### 2. **Join an Existing Session**
```javascript
// Join by lobby ID
window.socketClient.joinTroubleshootingLobby(lobbyId, password);
```

### 3. **Share Network Changes**
```javascript
// Update network topology
const changes = {
    action: 'add_device',
    devices: { 'router1': { type: 'router', x: 100, y: 100 } }
};

window.socketClient.updateNetworkTopology(changes);
```

## 📡 WebSocket Events

### **Lobby Management**
| Event | Direction | Description |
|-------|-----------|-------------|
| `create_troubleshooting_lobby` | Client → Server | Create new session |
| `join_troubleshooting_lobby` | Client → Server | Join existing session |
| `leave_troubleshooting_lobby` | Client → Server | Leave current session |
| `get_public_lobbies` | Client → Server | Get available sessions |

### **Real-time Collaboration**
| Event | Direction | Description |
|-------|-----------|-------------|
| `update_cursor_position` | Client → Server | Share cursor position |
| `cursor_moved` | Server → Client | Receive cursor updates |
| `update_network_topology` | Client → Server | Share network changes |
| `network_topology_updated` | Server → Client | Receive network updates |
| `send_lobby_chat` | Client → Server | Send chat message |
| `lobby_chat_message` | Server → Client | Receive chat messages |

## 🎯 Usage Examples

### **Creating a Team Session**

1. **Click "Start Collaborative Session"** in the troubleshooting interface
2. **Configure your session**:
   - Session name: "Advanced EIGRP Lab"
   - Difficulty: Hard
   - Scenario: Route Flapping
   - Max participants: 4
   - Private: No
3. **Click "Create Session"** - you're now the session host!

### **Joining a Team Session**

1. **Click "Start Collaborative Session"**
2. **Browse available sessions** in the lobby browser
3. **Click on a session** to join instantly
4. **Start collaborating** with your teammates!

### **Real-time Collaboration**

- **See teammates' cursors** moving in real-time with color-coded labels
- **Watch network changes** as teammates add/remove devices and connections
- **Chat with your team** using the integrated messaging system
- **Track progress together** with shared completion indicators

## 🔧 Configuration

### **Lobby Settings**
```python
# Lobby configuration options
{
    'name': 'Session Name',              # Display name
    'scenario_type': 'easy|medium|hard', # Difficulty level
    'scenario_id': 'network|passive|...',# Specific scenario
    'max_participants': 2-8,             # Team size limit
    'is_private': True/False,            # Public or private
    'password': 'optional_password'      # For private sessions
}
```

### **Performance Settings**
```python
# Lobby manager settings
CLEANUP_INTERVAL = 300        # 5 minutes
MAX_CHAT_HISTORY = 100       # Messages to keep
MAX_NETWORK_HISTORY = 50     # Network changes to track
CURSOR_UPDATE_THROTTLE = 50  # 20 FPS cursor updates
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_collaborative_troubleshooting.py
```

**Test Coverage:**
- ✅ Lobby creation and management
- ✅ Multi-user session joining
- ✅ Real-time cursor tracking
- ✅ Network topology synchronization
- ✅ Chat messaging system
- ✅ Progress tracking
- ✅ Data serialization for WebSocket
- ✅ Error handling and edge cases

## 🔍 Monitoring & Administration

### **Admin Dashboard Integration**
- View all active collaborative sessions
- Monitor participant activity
- Force-close problematic sessions
- View session statistics and usage metrics

### **Automatic Cleanup**
- Inactive sessions are automatically closed after 4 hours
- Participants are removed after 30 minutes of inactivity
- Chat history and network changes are automatically pruned

## 🌐 API Reference

### **REST Endpoints**

#### `GET /api/troubleshooting/collaborative/lobbies`
Get list of public lobbies available for joining.

#### `POST /api/troubleshooting/collaborative/lobby`
Create a new collaborative troubleshooting session.

#### `GET /api/troubleshooting/collaborative/my-lobby`
Get current user's active lobby information.

#### `GET /api/troubleshooting/collaborative/stats`
Get system statistics for lobby usage.

## 🎨 UI Components

### **Lobby Browser Modal**
- Grid layout showing available sessions
- Session information: name, participants, difficulty, creator
- Quick join functionality with password support
- Create new session button

### **Collaboration Panel**
- Live participants list with status indicators
- Real-time chat with message history
- Leave session controls
- Color-coded user identification

### **User Cursors**
- Smooth cursor movement animation
- Username labels
- Unique colors per participant
- Non-intrusive design

## 🚀 Deployment Considerations

### **Scalability**
- Thread-safe lobby management
- Memory-efficient data structures
- Automatic cleanup of inactive resources
- WebSocket connection pooling

### **Security**
- User authentication required for all operations
- Private session password protection
- Admin controls for session management
- Input validation and sanitization

### **Performance**
- Throttled cursor updates (20 FPS)
- Efficient JSON serialization
- Minimal network overhead
- Optimized WebSocket message routing

## 🎉 Benefits

### **For Students**
- **Collaborative Learning**: Work together to solve complex network problems
- **Real-time Feedback**: Get immediate help from teammates
- **Social Learning**: Learn from observing teammates' approaches
- **Team Building**: Develop communication and collaboration skills

### **For Educators**
- **Group Projects**: Assign collaborative troubleshooting exercises
- **Peer Learning**: Students learn from each other
- **Assessment**: Observe team dynamics and individual contributions
- **Engagement**: Increased student engagement through collaboration

### **For Organizations**
- **Team Training**: Collaborative skill development
- **Remote Learning**: Effective distance learning capabilities
- **Knowledge Sharing**: Spread expertise across team members
- **Problem Solving**: Leverage collective intelligence

---

## 🎯 **Ready to Collaborate!**

The system is fully implemented and ready for real-time collaborative troubleshooting. Students can now work together like in Figma and Canva, making network troubleshooting a truly collaborative and engaging experience!
