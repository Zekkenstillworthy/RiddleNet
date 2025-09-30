# PowerShell script to deploy RiddleNet to EC2
# Usage: ./deploy_to_ec2.ps1

$ErrorActionPreference = "Stop"

# Configuration
$EC2_IP = "13.54.250.227"
$KEY_FILE = "riddlenet.pem"
$PROJECT_NAME = "riddlenet"

# Function to test SSH connection with different users
function Test-SSHUsers {
    $users = @("ubuntu", "ec2-user", "admin", "centos", "debian")
    
    foreach ($user in $users) {
        Write-Host "Testing SSH with user: $user" -ForegroundColor Yellow
        try {
            $result = ssh -i $KEY_FILE -o ConnectTimeout=5 -o BatchMode=yes "${user}@${EC2_IP}" "whoami" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Success! Connected with user: $user" -ForegroundColor Green
                return $user
            }
        }
        catch {
            # Continue to next user
        }
    }
    
    Write-Host "❌ Failed to connect with any standard user" -ForegroundColor Red
    return $null
}

# Function to create deployment archive
function Create-DeploymentArchive {
    Write-Host "Creating deployment archive..." -ForegroundColor Blue
    
    # Create temp directory for clean deployment
    $tempDir = "deployment_temp"
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $tempDir | Out-Null
    
    # Copy essential files (excluding dev files)
    $filesToCopy = @(
        "*.py",
        "requirements.txt",
        "gunicorn.conf.py",
        "wsgi.py",
        "Procfile",
        "admin",
        "api", 
        "config",
        "services",
        "static",
        "templates",
        "user",
        "utils",
        "migrations",
        "instance",
        "deployment/nginx",
        "deployment/systemd"
    )
    
    foreach ($pattern in $filesToCopy) {
        if ($pattern.Contains("/")) {
            # Directory
            $source = $pattern
            if (Test-Path $source) {
                $dest = Join-Path $tempDir (Split-Path $pattern -Leaf)
                Copy-Item $source $dest -Recurse -Force
            }
        } else {
            # Files
            Get-ChildItem -Path . -Filter $pattern | ForEach-Object {
                Copy-Item $_.FullName (Join-Path $tempDir $_.Name)
            }
        }
    }
    
    Write-Host "✅ Deployment archive created in $tempDir" -ForegroundColor Green
    return $tempDir
}

# Main deployment process
Write-Host "🚀 Starting RiddleNet Deployment to EC2" -ForegroundColor Cyan
Write-Host "Target: $EC2_IP" -ForegroundColor Cyan

# Test SSH connection
Write-Host "`n1. Testing SSH Connection..." -ForegroundColor Blue
$sshUser = Test-SSHUsers

if (-not $sshUser) {
    Write-Host "Cannot establish SSH connection. Please check:" -ForegroundColor Red
    Write-Host "- EC2 instance is running" -ForegroundColor Yellow
    Write-Host "- Security group allows SSH (port 22) from your IP" -ForegroundColor Yellow
    Write-Host "- SSH key matches the one used when creating EC2 instance" -ForegroundColor Yellow
    Write-Host "- Try connecting manually: ssh -i $KEY_FILE ubuntu@$EC2_IP" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n2. SSH Connection successful with user: $sshUser" -ForegroundColor Green

# Get system info
Write-Host "`n3. Getting system information..." -ForegroundColor Blue
$systemInfo = ssh -i $KEY_FILE "${sshUser}@${EC2_IP}" "uname -a && python3 --version 2>&1 || echo 'Python3 not installed'"
Write-Host $systemInfo -ForegroundColor Gray

# Create deployment archive
Write-Host "`n4. Preparing deployment files..." -ForegroundColor Blue
$deployDir = Create-DeploymentArchive

# Upload files to EC2
Write-Host "`n5. Uploading files to EC2..." -ForegroundColor Blue
ssh -i $KEY_FILE "${sshUser}@${EC2_IP}" "mkdir -p ~/$PROJECT_NAME"
scp -i $KEY_FILE -r "$deployDir\*" "${sshUser}@${EC2_IP}:~/$PROJECT_NAME/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Files uploaded successfully" -ForegroundColor Green
} else {
    Write-Host "❌ File upload failed" -ForegroundColor Red
    exit 1
}

# Clean up temp directory
Remove-Item $deployDir -Recurse -Force

Write-Host "`n🎉 Deployment preparation complete!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. SSH to EC2: ssh -i $KEY_FILE ${sshUser}@${EC2_IP}" -ForegroundColor White
Write-Host "2. Run the installation script: cd $PROJECT_NAME && sudo ./deployment/deploy.sh" -ForegroundColor White