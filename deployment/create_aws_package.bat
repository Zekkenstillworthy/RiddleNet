@echo off
echo Creating RiddleNet AWS deployment package...

set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%-%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

set PACKAGE_NAME=riddlenet-aws-deploy-%TIMESTAMP%.zip
set DEPLOY_DIR=%~dp0
set ROOT_DIR=%DEPLOY_DIR%\..

echo Package name: %PACKAGE_NAME%
echo Deploy directory: %DEPLOY_DIR%
echo Root directory: %ROOT_DIR%

cd /d "%ROOT_DIR%"

echo Creating deployment package...

REM Use PowerShell to create a zip file excluding specified files
powershell -Command "& { Add-Type -A 'System.IO.Compression.FileSystem'; [IO.Compression.ZipFile]::CreateFromDirectory('%ROOT_DIR%', '%DEPLOY_DIR%\%PACKAGE_NAME%'); }"

if %ERRORLEVEL% EQU 0 (
    echo ✅ Deployment package created successfully: %PACKAGE_NAME%
    echo 📁 Location: %DEPLOY_DIR%\%PACKAGE_NAME%
    echo.
    echo Next steps:
    echo 1. Upload to Elastic Beanstalk console
    echo 2. Configure environment variables
    echo 3. Deploy to environment
) else (
    echo ❌ Error creating deployment package
)

pause
