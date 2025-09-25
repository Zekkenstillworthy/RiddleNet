
@echo off
echo RiddleNet AWS Deployment Script
echo ================================

REM Check if EB CLI is installed
eb --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: EB CLI is not installed
    echo Please run install_aws_tools.bat first
    pause
    exit /b 1
)

REM Check if AWS CLI is configured
aws sts get-caller-identity >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: AWS CLI is not configured
    echo Please run: aws configure
    pause
    exit /b 1
)

echo Current AWS Identity:
aws sts get-caller-identity

set /p CONFIRM="Continue with deployment? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo Deployment cancelled
    pause
    exit /b 0
)

echo.
echo Step 1: Creating deployment package...
if exist deployment_package.zip del deployment_package.zip

REM Create a temporary directory for deployment
if exist temp_deploy rmdir /s /q temp_deploy
mkdir temp_deploy

REM Copy application files
echo Copying application files...
xcopy /s /e /q *.py temp_deploy\
xcopy /s /e /q admin temp_deploy\admin\
xcopy /s /e /q config temp_deploy\config\
xcopy /s /e /q services temp_deploy\services\
xcopy /s /e /q static temp_deploy\static\
xcopy /s /e /q templates temp_deploy\templates\
xcopy /s /e /q user temp_deploy\user\
xcopy /s /e /q utils temp_deploy\utils\
xcopy /s /e /q migrations temp_deploy\migrations\
xcopy /s /e /q .ebextensions temp_deploy\.ebextensions\
xcopy /s /e /q .platform temp_deploy\.platform\
copy requirements.txt temp_deploy\

echo.
echo Step 2: Deploying to Elastic Beanstalk...
cd temp_deploy

REM Initialize EB if not already done
if not exist .elasticbeanstalk (
    echo Initializing Elastic Beanstalk application...
    eb init riddlenet --platform "Python 3.11" --region us-east-1
)

REM Deploy
echo Deploying application...
eb deploy

if %errorlevel% equ 0 (
    echo.
    echo ✅ Deployment successful!
    echo.
    echo Getting application URL...
    eb status | findstr "CNAME"
    echo.
    echo You can also check your application at:
    eb open
) else (
    echo ❌ Deployment failed. Check the logs with: eb logs
)

REM Cleanup
cd ..
rmdir /s /q temp_deploy

pause