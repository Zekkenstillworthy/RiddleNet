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

echo Creating deployment package with exclusions...

REM Create PowerShell script to exclude files
powershell -Command "& { $exclude = @('__pycache__', '.git', '.vscode', '.idea', '*.pyc', '*.pyo', '*.pyd', '*.log', '.env', 'node_modules', '*.zip', '*.bak', '*.tmp', '.pytest_cache', '.coverage', 'htmlcov', '.tox', 'venv', '.venv', 'run_local.py'); $source = '%ROOT_DIR%'; $destination = '%DEPLOY_DIR%\%PACKAGE_NAME%'; Add-Type -A 'System.IO.Compression.FileSystem'; $zip = [IO.Compression.ZipFile]::Open($destination, 'Create'); Get-ChildItem -Path $source -Recurse | Where-Object { $include = $true; foreach($ex in $exclude) { if($_.FullName -like '*' + $ex + '*') { $include = $false; break; } } $include } | ForEach-Object { $relativePath = $_.FullName.Substring($source.Length + 1); if($_.PSIsContainer -eq $false) { [IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $_.FullName, $relativePath) } }; $zip.Dispose(); }"

if %ERRORLEVEL% EQU 0 (
    echo ✅ Deployment package created successfully: %PACKAGE_NAME%
    echo 📁 Location: %DEPLOY_DIR%\%PACKAGE_NAME%
    echo.
    echo Contents included:
    echo - application.py (EB entry point)
    echo - requirements.txt (dependencies)
    echo - Procfile (process definition)
    echo - .ebextensions/ (EB configuration)
    echo - All application code and templates
    echo.
    echo Next steps:
    echo 1. Set environment variables in EB
    echo 2. Upload and deploy this package
    echo 3. Test the endpoints
) else (
    echo ❌ Error creating deployment package
)

pause