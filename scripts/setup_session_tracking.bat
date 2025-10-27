@echo off
REM Setup script for concurrent login prevention
REM This script runs the database migration to add session tracking tables

echo ========================================
echo RiddleNet - Session Tracking Setup
echo ========================================
echo.

echo This script will:
echo 1. Create user_sessions table
echo 2. Create instructor_sessions table
echo 3. Verify the tables were created successfully
echo.

set /p confirm="Do you want to continue? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo Setup cancelled.
    exit /b 0
)

echo.
echo Running database migration...
echo.

python migrations\007_add_session_tracking.py upgrade

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Migration completed successfully!
    echo ========================================
    echo.
    echo Session tracking is now enabled.
    echo Users can only be logged in from one device at a time.
    echo.
    echo Next steps:
    echo 1. Restart your RiddleNet application
    echo 2. Test login from multiple devices
    echo 3. Verify that previous sessions are terminated
    echo.
    echo For more information, see:
    echo archive\documentation\CONCURRENT_LOGIN_PREVENTION.md
    echo.
) else (
    echo.
    echo ========================================
    echo Migration failed!
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo Make sure:
    echo 1. Your database is running
    echo 2. Database credentials are correct
    echo 3. Python environment is activated
    echo.
)

pause
