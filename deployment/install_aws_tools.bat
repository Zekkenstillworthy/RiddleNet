@echo off
echo Installing AWS CLI and EB CLI...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Install AWS CLI
echo Installing AWS CLI...
pip install awscli

REM Install EB CLI
echo Installing Elastic Beanstalk CLI...
pip install awsebcli

REM Verify installations
echo Verifying installations...
aws --version
eb --version

if %errorlevel% equ 0 (
    echo.
    echo ✅ AWS CLI and EB CLI installed successfully!
    echo.
    echo Next steps:
    echo 1. Configure AWS credentials: aws configure
    echo 2. Initialize EB application: eb init
    echo 3. Create environment: eb create
    echo.
) else (
    echo ❌ Installation failed. Please check the error messages above.
)

pause