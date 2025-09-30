#!/bin/bash
# RiddleNet Deployment Script for AWS EC2 Ubuntu
# This script sets up and deploys RiddleNet on a fresh Ubuntu instance

set -e  # Exit on any error

# Configuration
APP_NAME="riddlenet"
APP_USER="ubuntu"
APP_GROUP="www-data"
APP_DIR="/opt/riddlenet"
DOMAIN_NAME="${DOMAIN_NAME:-your-domain.com}"
GIT_REPO="${GIT_REPO:-https://github.com/Zekkenstillworthy/RiddleNet.git}"
PYTHON_VERSION="3.11"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root. Please run as ubuntu user with sudo privileges."
   exit 1
fi

log "Starting RiddleNet deployment on AWS EC2..."

# Update system
log "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
log "Installing system dependencies..."
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    nginx \
    postgresql-client \
    git \
    curl \
    build-essential \
    libpq-dev \
    redis-tools \
    supervisor \
    certbot \
    python3-certbot-nginx \
    htop \
    ufw

# Create application directory
log "Setting up application directory..."
sudo mkdir -p $APP_DIR
sudo chown $APP_USER:$APP_GROUP $APP_DIR

# Clone or update repository
if [ -d "$APP_DIR/.git" ]; then
    log "Updating existing repository..."
    cd $APP_DIR
    git pull origin main
else
    log "Cloning repository..."
    git clone $GIT_REPO $APP_DIR
    cd $APP_DIR
    sudo chown -R $APP_USER:$APP_GROUP $APP_DIR
fi

# Create Python virtual environment
log "Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip and install requirements
log "Installing Python dependencies..."
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt

# Create necessary directories
log "Creating necessary directories..."
mkdir -p logs static/uploads instance

# Set up environment file if it doesn't exist
if [ ! -f ".env" ]; then
    log "Creating environment file from template..."
    cp .env.example .env
    warn "Please edit .env file with your actual configuration values!"
    warn "Especially: SECRET_KEY, DATABASE_URL, AWS credentials, S3_BUCKET"
fi

# Set up systemd service
log "Installing systemd service..."
sudo cp deployment/systemd/riddlenet.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable riddlenet

# Set up nginx configuration
log "Installing nginx configuration..."
sudo cp deployment/nginx/riddlenet.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/riddlenet.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Configure firewall
log "Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Set proper permissions
log "Setting file permissions..."
sudo chown -R $APP_USER:$APP_GROUP $APP_DIR
chmod +x $APP_DIR/venv/bin/*

# Create log rotation
log "Setting up log rotation..."
sudo tee /etc/logrotate.d/riddlenet > /dev/null <<EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $APP_USER $APP_GROUP
    postrotate
        systemctl reload riddlenet
    endscript
}
EOF

# Install SSL certificate (if domain is configured)
if [ "$DOMAIN_NAME" != "your-domain.com" ]; then
    log "Setting up SSL certificate for $DOMAIN_NAME..."
    # Update nginx config with actual domain
    sudo sed -i "s/your-domain.com/$DOMAIN_NAME/g" /etc/nginx/sites-available/riddlenet.conf
    
    # Get SSL certificate
    sudo certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME --non-interactive --agree-tos -m admin@$DOMAIN_NAME
else
    warn "Domain not configured. SSL setup skipped."
    warn "Update DOMAIN_NAME environment variable and run: sudo certbot --nginx"
fi

# Start services
log "Starting services..."
sudo systemctl restart nginx
sudo systemctl start riddlenet
sudo systemctl status riddlenet --no-pager -l

# Show service status
log "Deployment completed! Service status:"
echo "========================="
sudo systemctl is-active riddlenet && echo "✅ RiddleNet service is running" || echo "❌ RiddleNet service failed"
sudo systemctl is-active nginx && echo "✅ Nginx is running" || echo "❌ Nginx failed"
echo "========================="

# Show useful commands
log "Useful commands for management:"
echo "View logs:           sudo journalctl -u riddlenet -f"
echo "Restart service:     sudo systemctl restart riddlenet"
echo "Check status:        sudo systemctl status riddlenet"
echo "Reload nginx:        sudo systemctl reload nginx"
echo "View nginx logs:     sudo tail -f /var/log/nginx/riddlenet_error.log"

# Show next steps
log "Next steps:"
echo "1. Edit $APP_DIR/.env with your actual configuration"
echo "2. Set up your RDS database and update DATABASE_URL"
echo "3. Configure your S3 bucket and update S3_BUCKET"
echo "4. Run database migrations if needed"
echo "5. Test the application: curl -k https://$DOMAIN_NAME/health"

if [ "$DOMAIN_NAME" == "your-domain.com" ]; then
    warn "Remember to configure your domain name and SSL certificate!"
fi

log "Deployment script completed successfully!"