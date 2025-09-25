#!/bin/bash


# RiddleNet AWS Setup Script for Linux/Mac
echo "=== RiddleNet AWS Setup ==="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python installation
if ! command_exists python3; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install AWS CLI if not present
if ! command_exists aws; then
    echo "Installing AWS CLI..."
    python3 -m pip install awscli
else
    echo "✅ AWS CLI found: $(aws --version)"
fi

# Install EB CLI if not present
if ! command_exists eb; then
    echo "Installing EB CLI..."
    python3 -m pip install awsebcli
else
    echo "✅ EB CLI found: $(eb --version)"
fi

# Check AWS configuration
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "⚠️  AWS CLI not configured. Please run: aws configure"
    exit 1
fi

echo "✅ AWS Configuration verified"
aws sts get-caller-identity

echo ""
echo "🚀 Setup complete! You can now:"
echo "1. Run: eb init"
echo "2. Run: eb create"
echo "3. Run: eb deploy"