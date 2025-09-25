@echo off
echo Creating deployment package for AWS Elastic Beanstalk...

REM Change to parent directory (project root)
cd ..

REM Clean up any previous deployment package
if exist riddlenet-deploy.zip del riddlenet-deploy.zip
if exist deploy_temp rmdir /s /q deploy_temp

REM Create temporary deployment directory
mkdir deploy_temp

REM Copy essential files for EB deployment
echo Copying application files...
copy application.py deploy_temp\ 2>nul
copy requirements.txt deploy_temp\ 2>nul
copy __init__.py deploy_temp\ 2>nul
copy run.py deploy_temp\ 2>nul
copy socket_events.py deploy_temp\ 2>nul
copy socket_manager.py deploy_temp\ 2>nul

REM Copy configuration
if exist config xcopy /e /i config deploy_temp\config 2>nul
if exist .ebextensions xcopy /e /i .ebextensions deploy_temp\.ebextensions 2>nul
if exist .platform xcopy /e /i .platform deploy_temp\.platform 2>nul

REM Copy application directories
if exist admin xcopy /e /i admin deploy_temp\admin 2>nul
if exist services xcopy /e /i services deploy_temp\services 2>nul
if exist templates xcopy /e /i templates deploy_temp\templates 2>nul
if exist user xcopy /e /i user deploy_temp\user 2>nul
if exist utils xcopy /e /i utils deploy_temp\utils 2>nul
if exist instance xcopy /e /i instance deploy_temp\instance 2>nul
if exist migrations xcopy /e /i migrations deploy_temp\migrations 2>nul

REM Copy basic static files (main files are in S3)
if exist static xcopy /e /i static deploy_temp\static 2>nul

REM Create zip package
echo Creating zip package...
cd deploy_temp
powershell -command "Compress-Archive -Path * -DestinationPath ..\riddlenet-deploy.zip -Force"
cd ..

REM Clean up
rmdir /s /q deploy_temp

if exist riddlenet-deploy.zip (
    echo ✅ Deployment package created: riddlenet-deploy.zip
    echo Package size:
    dir riddlenet-deploy.zip
    echo.
    echo Next steps:
    echo 1. Go to AWS Elastic Beanstalk console
    echo 2. Create new application 'riddlenet'
    echo 3. Upload riddlenet-deploy.zip
    echo 4. Set environment variables from deployment\.env.production
) else (
    echo ❌ Failed to create deployment package
)

REM Return to deployment directory
cd deployment

pause