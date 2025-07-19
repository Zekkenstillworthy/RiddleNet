# RiddleNet - Educational Networking Platform

## Overview
RiddleNet is a comprehensive educational platform designed for teaching networking concepts through interactive exercises, quizzes, and hands-on topology building activities.

## Features
- **Interactive Topology Builder**: Visual network topology creation and configuration
- **Quiz System**: Comprehensive quiz management with multiple question types
- **User Management**: Student and admin authentication with role-based access
- **Real-time Notifications**: WebSocket-based notification system
- **Troubleshooting Scenarios**: Interactive network problem-solving exercises
- **Progress Tracking**: Detailed analytics and performance monitoring

## Architecture
- **Frontend**: HTML5, CSS3, JavaScript with WebSocket support
- **Backend**: Flask web framework with SQLAlchemy ORM
- **Database**: SQLite for development, easily configurable for production
- **Real-time Communication**: Flask-SocketIO for WebSocket connections
- **Authentication**: Flask-Login for session management

## Project Structure (Refactored)
```
RiddleNet/
├── admin/                          # Admin module for management interface
│   ├── controllers/               # Admin controllers
│   ├── models/                    # Admin data models
│   ├── routes/                    # Admin routing
│   ├── services/                  # Admin business logic
│   └── utils/                     # Admin utilities
├── user/                          # User module for main application
│   ├── models/                    # User data models
│   ├── routes/                    # User routing
│   ├── services/                  # User business logic
│   └── utils/                     # User utilities
├── static/                        # Static assets (CSS, JS, images)
├── templates/                     # Jinja2 templates
│   ├── admin/                     # Admin templates
│   └── user/                      # User templates
├── utils/                         # Shared utilities
├── services/                      # Shared services
├── instance/                      # Instance-specific files (databases)
├── docs/                          # Documentation
│   ├── current_docs/              # Active documentation
│   └── archived_docs/             # Historical documentation
├── scripts/                       # Utility scripts
├── archive/                       # Archived source materials
├── networking1_corrected_content.py  # Networking 1 course content
├── networking2_updated_content.py    # Networking 2 course content
├── run.py                         # Application entry point
├── socket_events.py               # WebSocket event handlers
├── socket_manager.py              # WebSocket management
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Zekkenstillworthy/RiddleNet.git
   cd RiddleNet
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```
   SECRET_KEY=your_secret_key_here
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   ```

5. **Initialize database**
   ```bash
   python run.py
   ```

## Usage

### Starting the Application
```bash
python run.py
```

The application will start on `http://localhost:5001` with WebSocket support.

### Admin Access
- Navigate to `/admin` for the admin panel
- Default admin credentials are created during database setup

### User Interface
- Main user interface is accessible at the root URL
- Students can register and access courses, quizzes, and topology exercises

## Configuration
- Database configuration is in `instance/config.py`
- Application settings can be modified in `__init__.py`
- WebSocket settings are configured in `socket_manager.py`

## Development
- The application uses Flask's development server with auto-reload
- WebSocket functionality is handled by Flask-SocketIO
- Database changes should be made through SQLAlchemy migrations

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License
This project is licensed under the MIT License - see the LICENSE file for details.
