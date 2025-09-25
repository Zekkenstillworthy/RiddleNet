# RiddleNet AWS Deployment Guide

This guide walks you through deploying RiddleNet to AWS using Elastic Beanstalk, RDS, and S3.

## Prerequisites

1. **AWS Account**: You need an active AWS account
2. **Python 3.8+**: Installed on your development machine
3. **Git**: For version control (optional but recommended)

## Architecture Overview

```
Internet → CloudFront → Application Load Balancer → EC2 Instances (Elastic Beanstalk)
                                                          ↓
                                                    RDS PostgreSQL
                                                          ↓
                                                    S3 (Static Files)
```

## Step 1: Prepare Your AWS Environment

### 1.1 Install AWS CLI and EB CLI

**Windows:**
```cmd
cd deployment
install_aws_tools.bat
```

**Linux/Mac:**
```bash
chmod +x deployment/setup_aws.sh
./deployment/setup_aws.sh
```

**Manual Installation:**
```bash
pip install awscli awsebcli
```

### 1.2 Configure AWS Credentials

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key  
- Default region (e.g., `us-east-1`)
- Default output format (`json`)

### 1.3 Verify Configuration

```bash
aws sts get-caller-identity
```

## Step 2: Set Up RDS Database

### 2.1 Create RDS PostgreSQL Instance

1. Go to AWS RDS Console
2. Click "Create database"
3. Choose "PostgreSQL"
4. Select "Production" or "Dev/Test" template
5. Configure:
   - **DB instance identifier**: `riddlenet-db`
   - **Master username**: `riddlenet_admin`
   - **Master password**: (choose a strong password)
   - **DB instance class**: `db.t3.micro` (for testing) or larger
   - **Storage**: 20 GB minimum
   - **VPC**: Default VPC
   - **Public access**: Yes (for initial setup)
   - **VPC security group**: Create new

6. Note down the endpoint URL after creation

### 2.2 Configure Security Group

1. Go to EC2 → Security Groups
2. Find the RDS security group
3. Add inbound rule:
   - Type: PostgreSQL
   - Port: 5432
   - Source: Your Elastic Beanstalk security group (or 0.0.0.0/0 temporarily)

## Step 3: Set Up S3 Bucket

### 3.1 Create S3 Bucket

```bash
aws s3 mb s3://riddlenet-static-files-[your-unique-suffix]
```

### 3.2 Configure Bucket Policy

Create a bucket policy for public read access:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::riddlenet-static-files-[your-suffix]/*"
        }
    ]
}
```

### 3.3 Upload Static Files

```bash
aws s3 sync static/ s3://riddlenet-static-files-[your-suffix]/static/
```

## Step 4: Deploy with Elastic Beanstalk

### 4.1 Initialize EB Application

```bash
eb init
```

Choose:
- Region: `us-east-1` (or your preferred region)
- Application name: `riddlenet`
- Platform: `Python 3.11`
- Use CodeCommit: No
- Set up SSH: Yes (recommended)

### 4.2 Create Environment

```bash
eb create riddlenet-prod
```

This will:
- Create EC2 instances
- Set up load balancer
- Configure auto-scaling
- Deploy your application

### 4.3 Set Environment Variables

```bash
eb setenv \
  SECRET_KEY="your-super-secret-key" \
  DATABASE_URL="postgresql://riddlenet_admin:password@your-rds-endpoint:5432/riddlenet" \
  RDS_HOSTNAME="your-rds-endpoint" \
  RDS_USERNAME="riddlenet_admin" \
  RDS_PASSWORD="your-password" \
  RDS_PORT="5432" \
  RDS_DB_NAME="riddlenet" \
  AWS_S3_BUCKET="riddlenet-static-files-your-suffix" \
  AWS_S3_REGION="us-east-1" \
  FLASK_ENV="production"
```

### 4.4 Deploy Application

**Using Script (Windows):**
```cmd
cd deployment
deploy.bat
```

**Manual Deployment:**
```bash
eb deploy
```

### 4.5 Verify Deployment

```bash
eb status
eb health
eb logs
```

Open your application:
```bash
eb open
```

## Step 5: Configure Domain and SSL (Optional)

### 5.1 Custom Domain

1. Go to Route 53
2. Create hosted zone for your domain
3. Create CNAME record pointing to your EB environment URL

### 5.2 SSL Certificate

1. Go to Certificate Manager
2. Request certificate for your domain
3. Validate domain ownership
4. Configure load balancer to use HTTPS

## Step 6: Production Optimizations

### 6.1 Database Optimization

1. **Connection Pooling**: Already configured in `config/production.py`
2. **Read Replicas**: Create if needed for high traffic
3. **Backup**: Enable automated backups

### 6.2 Performance Monitoring

1. **CloudWatch**: Monitor application metrics
2. **Application Insights**: Track performance
3. **Logging**: Use CloudWatch Logs for centralized logging

### 6.3 Security

1. **WAF**: Set up Web Application Firewall
2. **VPC**: Move RDS to private subnet
3. **IAM**: Use least privilege access
4. **Secrets Manager**: Store sensitive data

## Step 7: Maintenance Operations

### 7.1 Updating Application

```bash
# Deploy new version
eb deploy

# Check deployment status
eb status

# View logs if issues occur
eb logs
```

### 7.2 Database Migrations

```bash
# SSH into instance
eb ssh

# Run migrations
cd /var/app/current
source /var/app/venv/*/bin/activate
python -c "from application import application; from __init__ import db; application.app_context().push(); db.create_all()"
```

### 7.3 Scaling

```bash
# Scale up
eb scale 3

# Check auto-scaling
eb config
```

## Troubleshooting

### Common Issues

1. **Application Not Starting**
   - Check logs: `eb logs`
   - Verify environment variables
   - Check database connectivity

2. **Database Connection Errors**
   - Verify RDS security group
   - Check connection string
   - Ensure RDS is running

3. **Static Files Not Loading**
   - Verify S3 bucket permissions
   - Check S3 bucket policy
   - Ensure CORS is configured

4. **High Memory Usage**
   - Consider larger instance type
   - Optimize database queries
   - Review memory leaks

### Debug Commands

```bash
# View application logs
eb logs

# SSH into instance
eb ssh

# Check environment variables
eb printenv

# View configuration
eb config

# Check health
eb health
```

## Cost Optimization

1. **Right-sizing**: Start with smaller instances and scale up
2. **Reserved Instances**: For production workloads
3. **S3 Lifecycle**: Archive old static files
4. **CloudWatch**: Monitor and optimize based on metrics

## Security Checklist

- [ ] RDS in private subnet
- [ ] Security groups properly configured
- [ ] SSL/TLS enabled
- [ ] Environment variables secured
- [ ] WAF configured
- [ ] Backup strategy in place
- [ ] Monitoring and alerting set up

## Support

For issues related to:
- **AWS Services**: Check AWS documentation and support
- **RiddleNet Application**: Review application logs and code
- **Deployment**: Check this guide and EB documentation

---

## Quick Reference

### Useful Commands

```bash
# Deploy
eb deploy

# Check status
eb status

# View logs
eb logs

# Scale application
eb scale 2

# Open application
eb open

# SSH to instance
eb ssh

# Set environment variable
eb setenv KEY=VALUE

# Terminate environment
eb terminate
```

### Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `your-secret-key` |
| `DATABASE_URL` | Complete database URL | `postgresql://user:pass@host:5432/db` |
| `RDS_HOSTNAME` | RDS endpoint | `riddlenet.xyz.rds.amazonaws.com` |
| `RDS_USERNAME` | Database username | `riddlenet_admin` |
| `RDS_PASSWORD` | Database password | `your-secure-password` |
| `RDS_PORT` | Database port | `5432` |
| `RDS_DB_NAME` | Database name | `riddlenet` |
| `AWS_S3_BUCKET` | S3 bucket name | `riddlenet-static-files` |
| `AWS_S3_REGION` | S3 region | `us-east-1` |
| `FLASK_ENV` | Flask environment | `production` |