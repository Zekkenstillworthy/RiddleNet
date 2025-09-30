# 🚨 EC2 Connection Troubleshooting Guide

## Current Issue
Cannot connect to EC2 instance at `13.54.250.227` via SSH.

## Possible Causes & Solutions

### 1. EC2 Instance Not Running
**Check:** Go to AWS Console → EC2 → Instances → Check if instance is in "running" state
**Fix:** Start the instance if it's stopped

### 2. IP Address Changed
**Check:** EC2 instances with dynamic IPs change on reboot
**Fix:** Get current public IP from AWS Console → EC2 → Instance → Description tab

### 3. Security Group Issues
**Check:** Instance Security Group must allow:
- SSH (port 22) from your current public IP
- HTTP (port 80) from anywhere (0.0.0.0/0)
- HTTPS (port 443) from anywhere (0.0.0.0/0)

**Fix:** 
```bash
# Get your current public IP
curl -s https://checkip.amazonaws.com

# Add inbound rules in Security Group:
Type: SSH, Protocol: TCP, Port: 22, Source: YOUR_PUBLIC_IP/32
Type: HTTP, Protocol: TCP, Port: 80, Source: 0.0.0.0/0
Type: HTTPS, Protocol: TCP, Port: 443, Source: 0.0.0.0/0
```

### 4. Wrong SSH Key
**Check:** Ensure the `riddlenet.pem` key matches the one selected when creating the EC2 instance
**Fix:** Re-download the key pair from AWS if available, or create new instance with correct key

### 5. Wrong Username
**Common usernames by AMI type:**
- Amazon Linux 2/2023: `ec2-user`
- Ubuntu: `ubuntu`
- Debian: `admin` or `debian`
- CentOS: `centos`
- Red Hat: `ec2-user`

## 🔧 Quick Fix Commands

### Test Connectivity
```cmd
# Test if port 22 is open
telnet 13.54.250.227 22

# If instance IP changed, get new one from AWS Console
```

### Try Alternative Connection Methods
```cmd
# Try with different key format
ssh -i riddlenet.pem -o IdentitiesOnly=yes ubuntu@NEW_IP

# Try with full path
ssh -i "C:\full\path\to\riddlenet.pem" ubuntu@NEW_IP
```

## 🚀 Alternative Deployment Methods

### Option 1: AWS Session Manager (No SSH needed)
```bash
# Install AWS CLI and Session Manager plugin
aws ssm start-session --target INSTANCE_ID
```

### Option 2: EC2 User Data (Bootstrap)
Upload deployment script as User Data when launching new instance.

### Option 3: AWS CodeDeploy
Set up automatic deployment pipeline.

## 📝 What to Check in AWS Console

1. **EC2 Instance Status**
   - State: Should be "running"
   - Status Checks: Should be "2/2 checks passed"
   - Public IPv4: Note the current IP

2. **Security Group**
   - Inbound Rules: SSH (22) allowed from your IP
   - Outbound Rules: All traffic allowed (default)

3. **Key Pairs**
   - Verify the key name matches your `.pem` file

4. **VPC/Subnet**
   - Instance should be in public subnet
   - Route table should have internet gateway

## 🎯 Next Steps

1. **Check AWS Console** for instance status and current public IP
2. **Update IP address** in deployment script if it changed
3. **Verify Security Group** allows SSH from your current public IP  
4. **Test SSH connection** with correct IP and username
5. **Continue deployment** once connection is established

## 📞 Need Help?

If the issue persists:
1. Check AWS CloudTrail for any instance events
2. Review VPC Flow Logs if available
3. Contact AWS Support if it's an infrastructure issue
4. Consider creating a new EC2 instance with proper configuration

---

**Current Working Directory:** `c:\Users\gilbe\OneDrive\Desktop\RiddleNet - Copy - Copy (2)`
**SSH Key:** `riddlenet.pem` (permissions set correctly)
**Target IP:** `13.54.250.227` (⚠️ may have changed)