@echo off
echo Deploying admin and user modules to AWS EC2...

:: Set variables
set EC2_USER=ubuntu
set EC2_IP=54.206.121.66
set KEY_PATH=C:\Users\gilbe\OneDrive\Desktop\riddlenet-keypair.pem
set APP_DIR=/home/ubuntu/app

:: Create directories on EC2
echo Creating directories...
ssh -i "%KEY_PATH%" %EC2_USER%@%EC2_IP% "mkdir -p %APP_DIR%/admin/{api,config,controllers,models,routes,services,templates,utils}"
ssh -i "%KEY_PATH%" %EC2_USER%@%EC2_IP% "mkdir -p %APP_DIR%/user/{api,controllers,models,routes,utils}"
ssh -i "%KEY_PATH%" %EC2_USER%@%EC2_IP% "mkdir -p %APP_DIR%/services"
ssh -i "%KEY_PATH%" %EC2_USER%@%EC2_IP% "mkdir -p %APP_DIR%/utils"
ssh -i "%KEY_PATH%" %EC2_USER%@%EC2_IP% "mkdir -p %APP_DIR%/config"
ssh -i "%KEY_PATH%" %EC2_USER%@%EC2_IP% "mkdir -p %APP_DIR%/templates"
ssh -i "%KEY_PATH%" %EC2_USER%@%EC2_IP% "mkdir -p %APP_DIR%/static"
ssh -i "%KEY_PATH%" %EC2_USER%@%EC2_IP% "mkdir -p %APP_DIR%/instance"
ssh -i "%KEY_PATH%" %EC2_USER%@%EC2_IP% "mkdir -p %APP_DIR%/migrations"

:: Transfer admin module
echo Transferring admin module...
scp -i "%KEY_PATH%" -r admin/* %EC2_USER%@%EC2_IP%:%APP_DIR%/admin/

:: Transfer user module
echo Transferring user module...
scp -i "%KEY_PATH%" -r user/* %EC2_USER%@%EC2_IP%:%APP_DIR%/user/

:: Transfer services
echo Transferring services...
scp -i "%KEY_PATH%" -r services/* %EC2_USER%@%EC2_IP%:%APP_DIR%/services/

:: Transfer utils
echo Transferring utils...
scp -i "%KEY_PATH%" -r utils/* %EC2_USER%@%EC2_IP%:%APP_DIR%/utils/

:: Transfer config
echo Transferring config...
scp -i "%KEY_PATH%" -r config/* %EC2_USER%@%EC2_IP%:%APP_DIR%/config/

:: Transfer templates
echo Transferring templates...
scp -i "%KEY_PATH%" -r templates/* %EC2_USER%@%EC2_IP%:%APP_DIR%/templates/

:: Transfer static files
echo Transferring static files...
scp -i "%KEY_PATH%" -r static/* %EC2_USER%@%EC2_IP%:%APP_DIR%/static/

:: Transfer instance config
echo Transferring instance config...
scp -i "%KEY_PATH%" -r instance/* %EC2_USER%@%EC2_IP%:%APP_DIR%/instance/

:: Transfer migrations
echo Transferring migrations...
scp -i "%KEY_PATH%" -r migrations/* %EC2_USER%@%EC2_IP%:%APP_DIR%/migrations/

:: Transfer supporting files
echo Transferring supporting files...
scp -i "%KEY_PATH%" application.py %EC2_USER%@%EC2_IP%:%APP_DIR%/
scp -i "%KEY_PATH%" socket_events.py %EC2_USER%@%EC2_IP%:%APP_DIR%/
scp -i "%KEY_PATH%" socket_manager.py %EC2_USER%@%EC2_IP%:%APP_DIR%/
scp -i "%KEY_PATH%" __init__.py %EC2_USER%@%EC2_IP%:%APP_DIR%/

echo Transfer complete!
pause