# RiddleNet AWS Deployment Guide


## Deployment Package Ready ✅
- **File**: `riddlenet-deploy.zip` (2MB)
- **Location**: Project root directory
- **Contains**: All necessary application files and AWS configurations

## S3 Setup Complete ✅
- **Bucket**: `riddlenet-static-files-20250923`
- **Region**: `ap-southeast-2` (Asia Pacific - Sydney)
- **Static Files**: 137 files uploaded successfully
- **Access**: Public read access configured

## Next Steps: Deploy to Elastic Beanstalk

### 1. Access AWS Console
1. Go to [AWS Console](https://aws.amazon.com/console/)
2. Sign in with your credentials
3. Navigate to **Elastic Beanstalk** service

### 2. Create New Application
1. Click **"Create Application"**
2. **Application name**: `riddlenet-app`
3. **Platform**: Python 3.12
4. **Application code**: Upload your code
   - Select **"Upload your code"**
   - Click **"Choose file"** and select `riddlenet-deploy.zip`
5. Click **"Create application"**

### 3. Configure Environment Variables
After deployment, go to **Configuration** → **Software** and add:

```
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/riddlenet
SECRET_KEY=your-secret-key-here
S3_BUCKET_NAME=riddlenet-static-files-20250923
S3_REGION=ap-southeast-2
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
FLASK_ENV=production
SQLALCHEMY_DATABASE_URI=postgresql://username:password@your-rds-endpoint:5432/riddlenet
```

### 4. Create RDS Database
1. Go to **RDS** service
2. Click **"Create database"**
3. Choose **PostgreSQL**
4. **Template**: Production
5. **DB instance identifier**: `riddlenet-db`
6. **Database name**: `riddlenet`
7. Set username/password
8. **VPC**: Same as your EB environment
9. **Security group**: Allow connections from EB

### 5. Update Security Groups
- **RDS Security Group**: Allow inbound PostgreSQL (port 5432) from EB security group
- **EB Security Group**: Allow HTTP (80) and HTTPS (443) from anywhere

## Application Features Configured
- ✅ Socket.IO WebSocket support
- ✅ Static file serving from S3
- ✅ Health checks for load balancer
- ✅ Auto-scaling configuration
- ✅ Nginx optimization
- ✅ Database connection pooling
- ✅ Session management
- ✅ Security headers

## Important URLs After Deployment
- **Application**: `http://your-eb-environment.region.elasticbeanstalk.com`
- **Health Check**: `http://your-eb-environment.region.elasticbeanstalk.com/health`
- **Static Files**: `https://riddlenet-static-files-20250923.s3.ap-southeast-2.amazonaws.com/`

## Troubleshooting
- Check **Logs** in EB console for any errors
- Verify all environment variables are set correctly
- Ensure RDS security group allows EB connections
- Monitor **Health** dashboard for application status

## Cost Optimization
- **EB Environment**: t3.micro (free tier eligible)
- **RDS**: db.t3.micro (free tier eligible)
- **S3**: Pay per usage (minimal for static files)
- **Data Transfer**: Monitor usage

---
**Status**: Ready for deployment 🚀
**Package**: `riddlenet-deploy.zip` ready for upload