# RiddleNet Application

This is a Flask-based web application with WebSocket support for interactive quizzes and network topology challenges.

## Key Features

- Interactive quizzes with real-time feedback
- Network topology challenges with visual editor
- Troubleshooting scenarios for network learning
- WebSocket-based communication for real-time updates
- Dual-server architecture (WebSocket + Static Files)

## System Requirements

- Python 3.8+
- Required Python packages (see requirements.txt)

## Setup Instructions

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Configure environment variables in `.env` file:
```
SECRET_KEY=your_secret_key
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

3. Run the application:
```
python run.py
```

## Documentation

See the `/docs` directory for detailed documentation:

- Dual Server Architecture
- WebSocket Implementation
- Email Setup Instructions
- Troubleshooting Guide

## License

This project is licensed under the MIT License - see the LICENSE file for details.
