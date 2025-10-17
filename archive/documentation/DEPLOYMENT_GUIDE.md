# RiddleNet Production Deployment Guide

## 🚀 Overview

This guide provides step-by-step instructions for deploying RiddleNet to AWS EC2 with proper production configuration, including Flask-SocketIO WebSocket support, PostgreSQL (RDS), and S3 integration.

## ✅ Prerequisites

- AWS Account with permissions for EC2, RDS, S3
- Domain name (optional but recommended)
- Basic knowledge of Linux/Ubuntu commands

## 📋 Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
│   CloudFront    │    │     S3       │    │    Route53  │
│     (CDN)       │    │   (Static)   │    │    (DNS)    │
└─────────────────┘    └──────────────┘    └─────────────┘
         │                       │                   │
         └───────────────────────┼───────────────────┘
                                 │
┌─────────────────────────────────▼─────────────────────────────────┐
│                              EC2 Instance                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │    Nginx    │  │  Gunicorn   │  │ Flask-SocketIO│              │
│  │  (Reverse   │──│ (WSGI       │──│   (App +      │              │
│  │   Proxy)    │  │  Server)    │  │  WebSockets)  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘                │
└─────────────────────────────────┬─────────────────────────────────┘
                                  │
                         ┌────────▼────────┐
                         │   RDS PostgreSQL │
                         │   (Database)     │
                         └──────────────────┘
```

## 🔧 Step 1: Prepare Your Local Environment

### 1.1 Test Gunicorn Compatibility (Windows)

```cmd
# Run the test script to verify Gunicorn setup
test-gunicorn.bat
```

This will:
- Build a Docker image with your application
- Test Gunicorn + eventlet + Flask-SocketIO compatibility
- Verify all routes and WebSocket functionality

### 1.2 Initialize Database Migrations

```cmd
# Set up Flask-Migrate for production database management
python setup_migrations.py
```

## 🏗️ Step 2: Set Up AWS Infrastructure

### 2.1 Create RDS PostgreSQL Database

1. **Go to AWS RDS Console**
2. **Create Database:**
   - Engine: PostgreSQL
   - Version: 15.x (latest stable)
   - Template: Production (for prod) or Dev/Test (for testing)
   - DB Instance Class: `db.t3.micro` (free tier) or `db.t3.small`
   - Storage: 20 GB minimum, enable autoscaling
   - DB Name: `riddlenet_db`
   - Username: `riddlenet_user`
   - Password: Generate secure password
   - VPC: Default VPC or create new one
   - Subnet Group: Default
   - Public Access: No (security best practice)
   - Security Group: Create new one allowing PostgreSQL (5432) from EC2

3. **Note the endpoint:** `riddlenet-db.xxxxxx.us-east-1.rds.amazonaws.com`

### 2.2 Create S3 Bucket for Static Files

1. **Go to AWS S3 Console**
2. **Create Bucket:**
   - Name: `riddlenet-static-files` (must be globally unique)
   - Region: Same as your EC2 (e.g., us-east-1)
   - Block Public Access: Uncheck if serving public static files
   - Versioning: Enable (recommended)

3. **Set Bucket Policy** (for public static files):
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::riddlenet-static-files/*"
        }
    ]
}
```

### 2.3 Create EC2 Instance

1. **Launch Instance:**
   - AMI: Ubuntu Server 22.04 LTS
   - Instance Type: `t3.small` (minimum) or `t3.medium` (recommended)
   - Key Pair: Create new or use existing
   - Security Group: 
     - SSH (22) from your IP
     - HTTP (80) from anywhere (0.0.0.0/0)
     - HTTPS (443) from anywhere (0.0.0.0/0)
   - Storage: 20 GB minimum

2. **Assign Elastic IP** (optional but recommended)

## 🛠️ Step 3: Deploy to EC2

### 3.1 Connect to Your Instance

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 3.2 Run Automated Deployment

```bash
# Make deployment script executable and run
chmod +x deployment/deploy.sh

# Set environment variables for deployment
export DOMAIN_NAME="your-domain.com"
export GIT_REPO="https://github.com/Zekkenstillworthy/RiddleNet.git"

# Run deployment
./deployment/deploy.sh
```

### 3.3 Configure Environment Variables

```bash
# Edit the environment file
cd /opt/riddlenet
sudo nano .env
```

Update with your actual values:
```bash
# Flask Configuration
SECRET_KEY=your-super-secret-production-key
FLASK_ENV=production
FLASK_DEBUG=false

# Database (replace with your RDS endpoint)
DATABASE_URL=postgresql://riddlenet_user:your-password@riddlenet-db.xxxxxx.us-east-1.rds.amazonaws.com:5432/riddlenet_db

# AWS Configuration
AWS_REGION=us-east-1
S3_BUCKET=riddlenet-static-files

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### 3.4 Apply Database Migrations

```bash
# Activate virtual environment
source venv/bin/activate

# Apply database migrations
flask db upgrade

# If this is a fresh database, you might need to create initial migration
# flask db init (only if migrations folder doesn't exist)
# flask db migrate -m "Initial migration"
# flask db upgrade
```

### 3.5 Start the Application

```bash
# Start the application service
sudo systemctl start riddlenet
sudo systemctl enable riddlenet

# Check status
sudo systemctl status riddlenet

# View logs
sudo journalctl -u riddlenet -f
```

## 🔒 Step 4: Set Up SSL (HTTPS)

### 4.1 Configure Domain (if you have one)

1. **Point your domain to EC2 Elastic IP**
2. **Update nginx config:**
```bash
sudo sed -i 's/your-domain.com/actual-domain.com/g' /etc/nginx/sites-available/riddlenet.conf
```

### 4.2 Get SSL Certificate

```bash
# Install SSL certificate with Let's Encrypt
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Set up auto-renewal
sudo crontab -e
# Add this line:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔍 Step 5: Verify Deployment

### 5.1 Test Application

```bash
# Test health endpoint
curl https://your-domain.com/health

# Test WebSocket functionality (should return HTML with SocketIO)
curl https://your-domain.com/

# Check if static files load
curl https://your-domain.com/static/css/style.css
```

### 5.2 Monitor Logs

```bash
# Application logs
sudo journalctl -u riddlenet -f

# Nginx logs
sudo tail -f /var/log/nginx/riddlenet_error.log
sudo tail -f /var/log/nginx/riddlenet_access.log

# System logs
sudo tail -f /var/log/syslog
```

## 🚀 Step 6: Production Optimizations

### 6.1 Set Up Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop

# Set up log rotation (already configured by deploy script)
sudo logrotate -d /etc/logrotate.d/riddlenet
```

### 6.2 Database Backup

```bash
# Create backup script
cat > ~/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Create database backup
pg_dump $DATABASE_URL > $BACKUP_DIR/riddlenet_backup_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "riddlenet_backup_*.sql" -mtime +7 -delete
EOF

chmod +x ~/backup-db.sh

# Add to crontab for daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/backup-db.sh") | crontab -
```

## 🛡️ Security Checklist

- [ ] RDS database is not publicly accessible
- [ ] Security groups properly configured
- [ ] SSL certificate installed and auto-renewing
- [ ] Strong secret keys in environment variables
- [ ] Regular database backups configured
- [ ] System updates enabled
- [ ] Application logs being monitored

## 🚨 Troubleshooting

### Application Won't Start

```bash
# Check service status
sudo systemctl status riddlenet

# Check application logs
sudo journalctl -u riddlenet -n 50

# Check for missing dependencies
cd /opt/riddlenet
source venv/bin/activate
pip check
```

### WebSocket Issues

```bash
# Check nginx configuration
sudo nginx -t

# Verify WebSocket headers in nginx
grep -n "Upgrade" /etc/nginx/sites-available/riddlenet.conf
grep -n "Connection" /etc/nginx/sites-available/riddlenet.conf

# Test WebSocket connection manually
# Use browser developer tools to check for WebSocket upgrade (101 status)
```

### Database Connection Issues

```bash
# Test database connection
cd /opt/riddlenet
source venv/bin/activate
python -c "
import os
import psycopg2
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    print('Database connection successful')
    conn.close()
except Exception as e:
    print(f'Database connection failed: {e}')
"
```

### Performance Issues

```bash
# Monitor resource usage
htop
iotop

# Check nginx status
sudo systemctl status nginx

# Analyze gunicorn performance
ps aux | grep gunicorn
```

## 📞 Support

For additional support:
1. Check application logs first
2. Verify all environment variables are set correctly
3. Ensure AWS security groups allow required traffic
4. Test individual components (database, static files, etc.)

---

**🎉 Congratulations!** Your RiddleNet application should now be running in production with proper WebSocket support, SSL encryption, and scalable infrastructure!