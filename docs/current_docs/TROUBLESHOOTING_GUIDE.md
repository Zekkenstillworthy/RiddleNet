# Troubleshooting Module Integration Guide

This document provides information on the implementation and integration of the troubleshooting functionality in the application.

## Components

The troubleshooting module consists of:

1. **Admin Interface**:
   - Allows admins to create, edit, and manage troubleshooting scenarios
   - Configures scoring metrics, difficulty levels, and expected solutions
   - Provides preview functionality for testing scenarios

2. **User Interface**:
   - Displays available troubleshooting scenarios
   - Interactive topology editor for users to solve problems
   - Real-time scoring and feedback system

## Database Structure

The module uses two main tables:
- `troubleshooting` - Stores scenario details (title, description, expected solution, scoring metrics)
- `troubleshooting_progress` - Tracks user attempts and performance on scenarios

## Implementation

The module follows MVC architecture:

### Admin Side
- **Model**: `admin/models/troubleshooting.py` and `admin/models/troubleshooting_progress.py`
- **Controller**: `admin/controllers/troubleshooting_controller.py`
- **Routes**: `admin/routes/troubleshooting_routes.py` and `admin/routes/troubleshooting_api_routes.py`
- **Views**: `templates/admin/scenario.html` (integrated with existing scenario management)

### User Side
- **Controller**: `user/controllers/troubleshooting_controller.py`
- **Routes**: `user/routes/troubleshooting_routes.py`
- **Views**: `templates/user/troubleshooting.html`
- **Frontend**: JavaScript files in `static/js/user/troubleshooting.js` handling the interactive topology editor

## Routes

### Admin Routes
- `/admin/troubleshooting/` - Troubleshooting management dashboard
- `/admin/troubleshooting/api/list` - List all scenarios (paginated)
- `/admin/troubleshooting/api/preview` - Preview a scenario
- `/admin/troubleshooting/api/toggle-status` - Enable/disable a scenario
- `/admin/troubleshooting/api/stats` - Get statistics on scenario usage

### User Routes
- `/troubleshooting/` - Display available troubleshooting scenarios
- `/troubleshooting/api/{id}` - Get details of a specific scenario
- `/troubleshooting/api/submit` - Submit a solution for scoring

## Integration Notes

1. The troubleshooting routes are registered in `run.py`
2. The user interface is accessible from the main user navigation
3. Real-time topology visualization uses the same core library as the admin topology editor
4. Scoring algorithm considers:
   - Base score configured by admin
   - Time bonus for fast completion
   - Perfect match bonus based on solution accuracy

## Testing

Run the test script to verify proper integration:

```bash
python test_troubleshooting.py
```

## Further Development

- Enhance the topology comparison algorithm for more precise scoring
- Add more detailed analytics on user performance
- Implement guided troubleshooting options for educational purposes
