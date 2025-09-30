@echo off
REM create_deployment_package.bat - Create deployment package on Windows

echo 🚀 Creating RiddleNet Deployment Package

REM Configuration
set PACKAGE_NAME=riddlenet-deployment-%date:~-4,4%%date:~-10,2%%date:~-7,2%-%time:~0,2%%time:~3,2%%time:~6,2%
set PACKAGE_NAME=%PACKAGE_NAME: =0%
set TEMP_DIR=deployment_temp
set PROJECT_NAME=riddlenet

REM Clean previous temp directory
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"

REM Create temporary deployment directory
mkdir "%TEMP_DIR%\%PROJECT_NAME%"

echo 📦 Copying essential files...

REM Copy Python files
copy *.py "%TEMP_DIR%\%PROJECT_NAME%\" >nul 2>&1
copy requirements.txt "%TEMP_DIR%\%PROJECT_NAME%\" >nul 2>&1
copy gunicorn.conf.py "%TEMP_DIR%\%PROJECT_NAME%\" >nul 2>&1
copy Procfile "%TEMP_DIR%\%PROJECT_NAME%\" >nul 2>&1

REM Copy directories
for %%d in (admin api config services static templates user utils migrations instance) do (
    if exist "%%d" (
        echo   Copying %%d\
        xcopy "%%d" "%TEMP_DIR%\%PROJECT_NAME%\%%d\" /e /i /q >nul
    )
)

REM Copy deployment configurations
if exist "deployment" (
    echo   Copying deployment configs...
    mkdir "%TEMP_DIR%\%PROJECT_NAME%\deployment"
    if exist "deployment\nginx" xcopy "deployment\nginx" "%TEMP_DIR%\%PROJECT_NAME%\deployment\nginx\" /e /i /q >nul
    if exist "deployment\systemd" xcopy "deployment\systemd" "%TEMP_DIR%\%PROJECT_NAME%\deployment\systemd\" /e /i /q >nul
    if exist "deployment\deploy.sh" copy "deployment\deploy.sh" "%TEMP_DIR%\%PROJECT_NAME%\deployment\" >nul
)

REM Create environment template
echo   Creating environment template...
(
echo # RiddleNet Production Configuration
echo # Copy this to .env and update with your actual values
echo.
echo # Flask Configuration
echo FLASK_ENV=production
echo FLASK_DEBUG=false
echo SECRET_KEY=your-super-secret-key-change-this
echo HOST=0.0.0.0
echo PORT=8000
echo.
echo # Database Configuration ^(RDS PostgreSQL^)
echo DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/riddlenet
echo.
echo # AWS Configuration
echo AWS_ACCESS_KEY_ID=your-access-key
echo AWS_SECRET_ACCESS_KEY=your-secret-key
echo AWS_DEFAULT_REGION=us-east-1
echo.
echo # S3 Configuration ^(for static files^)
echo S3_BUCKET=your-s3-bucket-name
echo S3_REGION=us-east-1
echo.
echo # Application Configuration
echo ADMIN_EMAIL=admin@yourdomain.com
echo DEFAULT_ADMIN_PASSWORD=change-this-password
echo.
echo # Security
echo SSL_REDIRECT=true
echo FORCE_HTTPS=true
echo.
echo # Logging
echo LOG_LEVEL=INFO
echo LOG_FILE=/var/log/riddlenet/app.log
) > "%TEMP_DIR%\%PROJECT_NAME%\.env.template"

REM Create installation script
echo   Creating installation script...
(
echo #!/bin/bash
echo # RiddleNet Installation Script for Ubuntu/Debian
echo.
echo set -e
echo.
echo echo "🚀 Installing RiddleNet on $(hostname)"
echo.
echo # Update system
echo sudo apt update
echo.
echo # Install system dependencies
echo echo "📦 Installing system packages..."
echo sudo apt install -y \
echo     python3 \
echo     python3-pip \
echo     python3-venv \
echo     nginx \
echo     postgresql-client \
echo     git \
echo     curl \
echo     unzip \
echo     certbot \
echo     python3-certbot-nginx
echo.
echo # Create application user
echo if ! id "riddlenet" ^&^>/dev/null; then
echo     echo "👤 Creating riddlenet user..."
echo     sudo useradd -r -s /bin/bash -d /opt/riddlenet -m riddlenet
echo fi
echo.
echo # Create application directory
echo sudo mkdir -p /opt/riddlenet
echo sudo chown riddlenet:riddlenet /opt/riddlenet
echo.
echo # Copy application files
echo echo "📁 Copying application files..."
echo sudo cp -r . /opt/riddlenet/
echo sudo chown -R riddlenet:riddlenet /opt/riddlenet
echo.
echo # Switch to application user for Python setup
echo sudo -u riddlenet bash ^<^< 'PYTHON_SETUP'
echo cd /opt/riddlenet
echo.
echo # Create virtual environment
echo echo "🐍 Setting up Python virtual environment..."
echo python3 -m venv venv
echo source venv/bin/activate
echo.
echo # Install Python dependencies
echo pip install --upgrade pip
echo pip install -r requirements.txt
echo.
echo # Create logs directory
echo mkdir -p /opt/riddlenet/logs
echo PYTHON_SETUP
echo.
echo # Install systemd service
echo if [ -f "deployment/systemd/riddlenet.service" ]; then
echo     echo "⚙️ Installing systemd service..."
echo     sudo cp deployment/systemd/riddlenet.service /etc/systemd/system/
echo     sudo systemctl daemon-reload
echo     sudo systemctl enable riddlenet
echo fi
echo.
echo # Install nginx configuration
echo if [ -f "deployment/nginx/riddlenet.conf" ]; then
echo     echo "🌐 Installing nginx configuration..."
echo     sudo cp deployment/nginx/riddlenet.conf /etc/nginx/sites-available/
echo     sudo ln -sf /etc/nginx/sites-available/riddlenet.conf /etc/nginx/sites-enabled/
echo     sudo rm -f /etc/nginx/sites-enabled/default
echo     sudo nginx -t
echo fi
echo.
echo # Create log directories
echo sudo mkdir -p /var/log/riddlenet
echo sudo chown riddlenet:riddlenet /var/log/riddlenet
echo.
echo echo "✅ Installation complete!"
echo echo ""
echo echo "📝 Next steps:"
echo echo "1. Copy .env.template to .env and configure your settings"
echo echo "2. Set up your database and run migrations"
echo echo "3. Start the services:"
echo echo "   sudo systemctl start riddlenet"
echo echo "   sudo systemctl start nginx"
echo echo "4. Set up SSL with Let's Encrypt if needed"
echo echo ""
echo echo "🔍 Check status:"
echo echo "   sudo systemctl status riddlenet"
echo echo "   sudo journalctl -u riddlenet -f"
) > "%TEMP_DIR%\%PROJECT_NAME%\install.sh"

REM Create README
echo   Creating deployment README...
(
echo # RiddleNet Deployment Package
echo.
echo This package contains everything needed to deploy RiddleNet to your EC2 instance.
echo.
echo ## Quick Start
echo.
echo 1. Upload this package to your EC2 instance:
echo    ```bash
echo    scp -i your-key.pem %PROJECT_NAME%.tar.gz ubuntu@your-ec2-ip:~
echo    ```
echo.
echo 2. Extract and install:
echo    ```bash
echo    ssh -i your-key.pem ubuntu@your-ec2-ip
echo    tar -xzf %PROJECT_NAME%.tar.gz
echo    cd %PROJECT_NAME%
echo    sudo ./install.sh
echo    ```
echo.
echo 3. Configure environment:
echo    ```bash
echo    sudo cp .env.template /opt/riddlenet/.env
echo    sudo nano /opt/riddlenet/.env  # Edit with your settings
echo    ```
echo.
echo 4. Start services:
echo    ```bash
echo    sudo systemctl start riddlenet
echo    sudo systemctl start nginx
echo    ```
echo.
echo ## What's Included
echo.
echo - ✅ Complete RiddleNet application
echo - ✅ Production-ready Gunicorn + eventlet configuration
echo - ✅ Nginx reverse proxy with WebSocket support
echo - ✅ Systemd service for auto-start
echo - ✅ SSL-ready configuration
echo - ✅ Database migration scripts
echo - ✅ Environment template
echo - ✅ Automated installation script
) > "%TEMP_DIR%\%PROJECT_NAME%\README_DEPLOYMENT.md"

echo 📦 Creating archive...

REM Create tar.gz using PowerShell (if available) or 7zip (if available)
where tar >nul 2>&1
if %errorlevel% == 0 (
    tar -czf "%PACKAGE_NAME%.tar.gz" -C "%TEMP_DIR%" "%PROJECT_NAME%"
) else (
    where 7z >nul 2>&1
    if %errorlevel% == 0 (
        7z a -tgzip "%PACKAGE_NAME%.tar.gz" "%TEMP_DIR%\%PROJECT_NAME%\*"
    ) else (
        echo ⚠️ Neither tar nor 7zip found. Creating ZIP archive instead...
        powershell -command "Compress-Archive -Path '%TEMP_DIR%\%PROJECT_NAME%\*' -DestinationPath '%PACKAGE_NAME%.zip'"
        set ARCHIVE_NAME=%PACKAGE_NAME%.zip
    )
)

REM Clean up temp directory
rmdir /s /q "%TEMP_DIR%"

echo ✅ Deployment package created: %PACKAGE_NAME%
if exist "%PACKAGE_NAME%.tar.gz" (
    set ARCHIVE_NAME=%PACKAGE_NAME%.tar.gz
) else (
    set ARCHIVE_NAME=%PACKAGE_NAME%.zip
)

echo 📦 Archive: %ARCHIVE_NAME%
echo.
echo 🚀 Ready to deploy!
echo Upload to EC2: scp -i riddlenet.pem %ARCHIVE_NAME% ubuntu@your-ec2-ip:~
echo.
echo 🔧 Troubleshooting:
echo - Check EC2_TROUBLESHOOTING.md for connection issues
echo - Verify your EC2 instance is running and accessible
echo - Update IP address if your EC2 instance IP changed

pause