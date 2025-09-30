#!/bin/bash
# create_deployment_package.sh - Create clean deployment archive

set -e

echo "🚀 Creating RiddleNet Deployment Package"

# Configuration
PACKAGE_NAME="riddlenet-deployment-$(date +%Y%m%d-%H%M%S)"
TEMP_DIR="deployment_temp"
ARCHIVE_NAME="${PACKAGE_NAME}.tar.gz"

# Clean previous temp directory
if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

# Create temporary deployment directory
mkdir -p "$TEMP_DIR/$PACKAGE_NAME"
cd "$TEMP_DIR/$PACKAGE_NAME"

echo "📦 Copying essential files..."

# Copy Python files
cp ../../*.py . 2>/dev/null || true
cp ../../requirements.txt . 2>/dev/null || true
cp ../../gunicorn.conf.py . 2>/dev/null || true
cp ../../Procfile . 2>/dev/null || true

# Copy directories
for dir in admin api config services static templates user utils migrations instance; do
    if [ -d "../../$dir" ]; then
        echo "  Copying $dir/"
        cp -r "../../$dir" .
    fi
done

# Copy deployment configurations
if [ -d "../../deployment" ]; then
    echo "  Copying deployment configs..."
    mkdir -p deployment
    cp -r ../../deployment/nginx deployment/ 2>/dev/null || true
    cp -r ../../deployment/systemd deployment/ 2>/dev/null || true
    cp ../../deployment/deploy.sh deployment/ 2>/dev/null || true
fi

# Create environment template
echo "  Creating environment template..."
cat > .env.template << 'EOF'
# RiddleNet Production Configuration
# Copy this to .env and update with your actual values

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your-super-secret-key-change-this
HOST=0.0.0.0
PORT=8000

# Database Configuration (RDS PostgreSQL)
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/riddlenet

# AWS Configuration
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1

# S3 Configuration (for static files)
S3_BUCKET=your-s3-bucket-name
S3_REGION=us-east-1

# Application Configuration
ADMIN_EMAIL=admin@yourdomain.com
DEFAULT_ADMIN_PASSWORD=change-this-password

# Security
SSL_REDIRECT=true
FORCE_HTTPS=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/riddlenet/app.log
EOF

# Create installation script
echo "  Creating installation script..."
cat > install.sh << 'EOF'
#!/bin/bash
# RiddleNet Installation Script for Ubuntu/Debian

set -e

echo "🚀 Installing RiddleNet on $(hostname)"

# Update system
sudo apt update

# Install system dependencies
echo "📦 Installing system packages..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    postgresql-client \
    git \
    curl \
    unzip \
    certbot \
    python3-certbot-nginx

# Create application user
if ! id "riddlenet" &>/dev/null; then
    echo "👤 Creating riddlenet user..."
    sudo useradd -r -s /bin/bash -d /opt/riddlenet -m riddlenet
fi

# Create application directory
sudo mkdir -p /opt/riddlenet
sudo chown riddlenet:riddlenet /opt/riddlenet

# Copy application files
echo "📁 Copying application files..."
sudo cp -r . /opt/riddlenet/
sudo chown -R riddlenet:riddlenet /opt/riddlenet

# Switch to application user for Python setup
sudo -u riddlenet bash << 'PYTHON_SETUP'
cd /opt/riddlenet

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create logs directory
mkdir -p /opt/riddlenet/logs
PYTHON_SETUP

# Install systemd service
if [ -f "deployment/systemd/riddlenet.service" ]; then
    echo "⚙️ Installing systemd service..."
    sudo cp deployment/systemd/riddlenet.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable riddlenet
fi

# Install nginx configuration
if [ -f "deployment/nginx/riddlenet.conf" ]; then
    echo "🌐 Installing nginx configuration..."
    sudo cp deployment/nginx/riddlenet.conf /etc/nginx/sites-available/
    sudo ln -sf /etc/nginx/sites-available/riddlenet.conf /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo nginx -t
fi

# Create log directories
sudo mkdir -p /var/log/riddlenet
sudo chown riddlenet:riddlenet /var/log/riddlenet

echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Copy .env.template to .env and configure your settings"
echo "2. Set up your database and run migrations"
echo "3. Start the services:"
echo "   sudo systemctl start riddlenet"
echo "   sudo systemctl start nginx"
echo "4. Set up SSL with Let's Encrypt if needed"
echo ""
echo "🔍 Check status:"
echo "   sudo systemctl status riddlenet"
echo "   sudo journalctl -u riddlenet -f"
EOF

chmod +x install.sh

# Create README for deployment
cat > README_DEPLOYMENT.md << 'EOF'
# RiddleNet Deployment Package

This package contains everything needed to deploy RiddleNet to your EC2 instance.

## Quick Start

1. Upload this package to your EC2 instance:
   ```bash
   scp -i your-key.pem riddlenet-deployment-*.tar.gz ubuntu@your-ec2-ip:~
   ```

2. Extract and install:
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   tar -xzf riddlenet-deployment-*.tar.gz
   cd riddlenet-deployment-*
   sudo ./install.sh
   ```

3. Configure environment:
   ```bash
   sudo cp .env.template /opt/riddlenet/.env
   sudo nano /opt/riddlenet/.env  # Edit with your settings
   ```

4. Start services:
   ```bash
   sudo systemctl start riddlenet
   sudo systemctl start nginx
   ```

## What's Included

- ✅ Complete RiddleNet application
- ✅ Production-ready Gunicorn + eventlet configuration
- ✅ Nginx reverse proxy with WebSocket support
- ✅ Systemd service for auto-start
- ✅ SSL-ready configuration
- ✅ Database migration scripts
- ✅ Environment template
- ✅ Automated installation script

## Requirements

- Ubuntu 18.04+ or Debian 9+
- Python 3.8+
- PostgreSQL database (can be RDS)
- Domain name (for SSL)

## Architecture

```
Internet → Nginx (443/80) → Gunicorn (127.0.0.1:8000) → Flask-SocketIO App
                         → Static Files (S3 or local)
                         → PostgreSQL Database (RDS)
```

## Troubleshooting

Check logs:
```bash
sudo journalctl -u riddlenet -f
sudo tail -f /var/log/nginx/error.log
```

Test components:
```bash
# Test Gunicorn directly
sudo -u riddlenet /opt/riddlenet/venv/bin/gunicorn -c /opt/riddlenet/gunicorn.conf.py wsgi:application

# Test nginx config
sudo nginx -t

# Check process status
sudo systemctl status riddlenet nginx
```
EOF

# Go back to original directory
cd ../..

# Create the archive
echo "📦 Creating archive: $ARCHIVE_NAME"
tar -czf "$ARCHIVE_NAME" -C "$TEMP_DIR" "$PACKAGE_NAME"

# Clean up temp directory
rm -rf "$TEMP_DIR"

echo "✅ Deployment package created: $ARCHIVE_NAME"
echo "📦 Size: $(du -h "$ARCHIVE_NAME" | cut -f1)"
echo ""
echo "🚀 Ready to deploy!"
echo "Upload to EC2: scp -i riddlenet.pem $ARCHIVE_NAME ubuntu@your-ec2-ip:~"