
# AWS Deployment Checklist for RiddleNet

## Pre-Deployment Setup

### AWS Account Setup
- [ ] AWS account created and verified
- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] EB CLI installed (`pip install awsebcli`)
- [ ] IAM user created with appropriate permissions
- [ ] Access keys generated and configured

### Development Environment
- [ ] Application tested locally
- [ ] All dependencies listed in requirements.txt
- [ ] Environment variables identified
- [ ] Database schema finalized
- [ ] Static files organized

## Infrastructure Setup

### RDS Database
- [ ] PostgreSQL RDS instance created
- [ ] Security group configured (port 5432)
- [ ] Database credentials stored securely
- [ ] Initial database and user created
- [ ] Connection tested from local machine

### S3 Bucket
- [ ] S3 bucket created with unique name
- [ ] Bucket policy configured for public read
- [ ] CORS configuration set if needed
- [ ] Static files uploaded to bucket
- [ ] CloudFront distribution created (optional)

### Elastic Beanstalk
- [ ] EB application initialized (`eb init`)
- [ ] Environment created (`eb create`)
- [ ] Load balancer type configured (Application)
- [ ] Instance type selected (t3.small minimum)
- [ ] Auto-scaling configured

## Application Configuration

### Environment Variables
- [ ] SECRET_KEY set (strong, unique)
- [ ] DATABASE_URL configured
- [ ] RDS_* variables set
- [ ] AWS_S3_* variables set
- [ ] FLASK_ENV=production
- [ ] MAIL_* variables set (if using email)
- [ ] LOG_LEVEL set appropriately

### Security Configuration
- [ ] HTTPS enabled (SSL certificate)
- [ ] Security groups properly configured
- [ ] Database in private subnet (recommended)
- [ ] WAF configured (optional)
- [ ] VPC configuration reviewed

## Deployment Process

### Pre-Deployment Checks
- [ ] Code committed to version control
- [ ] Requirements.txt updated
- [ ] Configuration files reviewed
- [ ] Database migrations prepared
- [ ] Static files synced to S3

### Deployment Steps
- [ ] `eb deploy` executed successfully
- [ ] Application health checked (`eb health`)
- [ ] Logs reviewed (`eb logs`)
- [ ] Application URL accessible (`eb open`)
- [ ] Database connectivity verified
- [ ] Static files loading correctly

### Post-Deployment Verification
- [ ] All application features tested
- [ ] User authentication working
- [ ] Database operations functional
- [ ] File uploads working (if applicable)
- [ ] WebSocket connections working
- [ ] Performance metrics reviewed

## Production Optimization

### Performance
- [ ] Database connection pooling enabled
- [ ] Static file caching configured
- [ ] Application performance profiled
- [ ] CloudWatch metrics enabled
- [ ] Auto-scaling triggers configured

### Monitoring
- [ ] CloudWatch alarms set up
- [ ] Log aggregation configured
- [ ] Health check endpoints working
- [ ] Error tracking enabled
- [ ] Performance monitoring in place

### Backup and Recovery
- [ ] RDS automated backups enabled
- [ ] S3 versioning enabled
- [ ] Disaster recovery plan documented
- [ ] Backup restoration tested
- [ ] Point-in-time recovery tested

### Security
- [ ] All secrets moved to environment variables
- [ ] Database access restricted
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] Vulnerability scanning enabled

## Maintenance Procedures

### Regular Tasks
- [ ] Log monitoring procedures documented
- [ ] Deployment procedures documented
- [ ] Rollback procedures tested
- [ ] Scaling procedures documented
- [ ] Backup verification scheduled

### Emergency Procedures
- [ ] Incident response plan created
- [ ] Emergency contacts identified
- [ ] Recovery procedures documented
- [ ] Communication plan established
- [ ] Rollback triggers defined

## Cost Management

### Cost Optimization
- [ ] Instance types optimized
- [ ] Auto-scaling policies tuned
- [ ] S3 lifecycle policies configured
- [ ] Reserved instances considered
- [ ] Cost monitoring alerts set

### Budget Controls
- [ ] AWS budgets created
- [ ] Billing alerts configured
- [ ] Resource tagging implemented
- [ ] Cost allocation tracking enabled
- [ ] Regular cost reviews scheduled

## Documentation

### Technical Documentation
- [ ] Architecture diagram created
- [ ] Deployment procedures documented
- [ ] Configuration management documented
- [ ] Troubleshooting guide created
- [ ] API documentation updated

### Operational Documentation
- [ ] Runbook created
- [ ] Monitoring procedures documented
- [ ] Maintenance windows defined
- [ ] Change management process documented
- [ ] Team access and responsibilities defined

---

## Quick Commands Reference

```bash
# Initialize EB app
eb init riddlenet --platform "Python 3.11" --region us-east-1

# Create environment
eb create riddlenet-prod

# Set environment variables
eb setenv SECRET_KEY="your-key" DATABASE_URL="postgresql://..."

# Deploy application
eb deploy

# Check status
eb status
eb health
eb logs

# Open application
eb open

# Scale application
eb scale 3

# SSH to instance
eb ssh
```

## Environment Variables Template

```bash
SECRET_KEY=your-super-secret-key
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@host:5432/db
RDS_HOSTNAME=your-rds-endpoint
RDS_USERNAME=riddlenet_admin
RDS_PASSWORD=your-password
RDS_PORT=5432
RDS_DB_NAME=riddlenet
AWS_S3_BUCKET=your-bucket-name
AWS_S3_REGION=us-east-1
```