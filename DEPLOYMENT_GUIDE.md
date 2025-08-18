# PDF Unlock API - Deployment Guide

This guide covers deploying the PDF Unlock API to AWS EC2 using various methods.

## 🚀 Quick Start

### Option 1: Automated Build and Deploy (Recommended)

1. **Build the deployment package:**

   ```bash
   # On Linux/Mac
   ./build.sh

   # On Windows
   build.bat
   ```

2. **Upload to EC2 and deploy:**

   ```bash
   # Copy build directory to EC2
   scp -r build/ ubuntu@your-ec2-ip:/tmp/

   # SSH to EC2 and deploy
   ssh ubuntu@your-ec2-ip
   sudo /tmp/build/deploy.sh
   ```

### Option 2: Amazon Linux EC2 with User Data

1. **Launch EC2 instance with user data:**

   - Use the `ec2-user-data-amazon-linux.sh` script in the "User data" field
   - This automatically sets up the environment when the instance starts

2. **Deploy application:**
   ```bash
   # Use the build script or manually deploy
   sudo /var/pdf-api/deploy-amazon-linux.sh
   ```

### Option 3: Docker Deployment

1. **Build and run with Docker:**
   ```bash
   cd build
   docker-compose up -d
   ```

## 📋 Prerequisites

### AWS Requirements

- AWS Account with EC2 access
- Key pair for SSH access
- Security group configured for SSH, HTTP, HTTPS, and port 8000

### Local Requirements

- Python 3.8+
- Git
- SSH client

## 🏗️ Build Process

The build scripts create a complete deployment package:

```
build/
├── app/                    # Application source code
├── config/                 # Production configuration
├── deploy.sh              # Main deployment script
├── pdf-api.service        # Systemd service file
├── nginx.conf             # Nginx configuration
├── gunicorn.conf.py       # Gunicorn configuration
├── Dockerfile             # Docker container definition
├── docker-compose.yml     # Multi-container setup
├── .env.template          # Environment variables template
├── deploy-config.json     # Deployment configuration
└── BUILD_SUMMARY.md       # Build documentation
```

## 🔧 Manual Deployment Steps

### 1. EC2 Instance Setup

Launch an Amazon Linux 2023 instance with:

- **Instance Type**: t3.micro (free tier) or t3.small for production
- **Storage**: 20GB GP3 volume
- **Security Groups**: Allow SSH (22), HTTP (80), HTTPS (443), and port 8000
- **User Data**: Use the `ec2-user-data-amazon-linux.sh` script for automatic setup

### 2. Install Dependencies

```bash
# Update system
sudo yum update -y

# Install required packages
sudo yum install -y python3 python3-pip python3-devel nginx curl

# Create application user
sudo useradd -r -s /bin/false -d /var/pdf-api pdf-api
sudo mkdir -p /var/pdf-api
sudo chown pdf-api:pdf-api /var/pdf-api
```

### 3. Deploy Application

```bash
# Copy application files
sudo cp -r app/ /var/pdf-api/
sudo cp requirements_simple.txt /var/pdf-api/requirements.txt

# Set permissions
sudo chown -R pdf-api:pdf-api /var/pdf-api
sudo chmod -R 755 /var/pdf-api

# Create virtual environment
cd /var/pdf-api
sudo -u pdf-api python3 -m venv venv
sudo -u pdf-api venv/bin/pip install -r requirements.txt
sudo -u pdf-api venv/bin/pip install gunicorn
```

### 4. Configure Services

```bash
# Install systemd service
sudo cp pdf-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pdf-api

# Configure nginx
sudo cp nginx.conf /etc/nginx/conf.d/pdf-api.conf
sudo rm -f /etc/nginx/conf.d/default.conf
sudo nginx -t
```

### 5. Start Services

```bash
# Start application
sudo systemctl start pdf-api
sudo systemctl status pdf-api

# Start nginx
sudo systemctl restart nginx
sudo systemctl status nginx
```

## 🐳 Docker Deployment

### Single Container

```bash
cd build
docker build -t pdf-api .
docker run -d -p 8000:8000 --name pdf-api pdf-api
```

### Multi-Container with Docker Compose

```bash
cd build
docker-compose up -d
```

### Production Docker Compose

```bash
# Create production environment file
cp .env.template .env
# Edit .env with production values

# Deploy with production settings
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## ☁️ Amazon Linux EC2 Setup

### Launch Instance with User Data

1. **Launch EC2 instance:**

   - Choose Amazon Linux 2023 AMI
   - Select your desired instance type
   - Configure security groups for SSH, HTTP, HTTPS, and port 8000
   - In "Advanced details" → "User data", paste the contents of `ec2-user-data-amazon-linux.sh`

2. **Wait for initialization:**
   - The user data script will run automatically
   - Check `/var/log/user-data.log` for progress
   - Instance will be ready when you see "Setup complete!"

### Manual Setup (Alternative)

If you prefer to set up manually instead of using user data:

```bash
# Run the setup script manually
sudo /var/pdf-api/deploy-amazon-linux.sh
```

## 🔒 Security Configuration

### Firewall Setup

```bash
# Configure firewalld (Amazon Linux)
sudo systemctl start firewalld
sudo systemctl enable firewalld
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### SSL/HTTPS Setup

```bash
# Install Certbot
sudo yum install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Environment Variables

```bash
# Create production environment file
sudo -u pdf-api cp .env.template .env
sudo -u pdf-api nano .env

# Set secure values
API_KEY=your-secure-api-key-here
CORS_ORIGINS=https://yourdomain.com
```

## 📊 Monitoring and Logs

### Service Status

```bash
# Check service status
sudo systemctl status pdf-api
sudo systemctl status nginx

# View logs
sudo journalctl -u pdf-api -f
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Health Checks

```bash
# Manual health check
curl -f http://localhost:8000/health

# Automated monitoring
/usr/local/bin/health-check.sh
/usr/local/bin/monitor-pdf-api.sh
```

### Log Rotation

```bash
# Check log rotation configuration
sudo cat /etc/logrotate.d/pdf-api

# Manual log rotation
sudo logrotate -f /etc/logrotate.d/pdf-api
```

## 🔄 Updates and Maintenance

### Application Updates

```bash
# Stop service
sudo systemctl stop pdf-api

# Backup current version
sudo cp -r /var/pdf-api /var/pdf-api.backup.$(date +%Y%m%d)

# Deploy new version
sudo cp -r new-app/ /var/pdf-api/
sudo chown -R pdf-api:pdf-api /var/pdf-api

# Update dependencies
cd /var/pdf-api
sudo -u pdf-api venv/bin/pip install -r requirements.txt

# Restart service
sudo systemctl start pdf-api
sudo systemctl status pdf-api
```

### System Updates

```bash
# Update system packages
sudo yum update -y

# Restart services if needed
sudo systemctl restart pdf-api
sudo systemctl restart nginx
```

## 🚨 Troubleshooting

### Common Issues

#### Service Won't Start

```bash
# Check service status
sudo systemctl status pdf-api

# View detailed logs
sudo journalctl -u pdf-api -n 50

# Check permissions
ls -la /var/pdf-api/
sudo chown -R pdf-api:pdf-api /var/pdf-api
```

#### Nginx Issues

```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Restart nginx
sudo systemctl restart nginx
```

#### Permission Issues

```bash
# Fix ownership
sudo chown -R pdf-api:pdf-api /var/pdf-api

# Fix permissions
sudo chmod -R 755 /var/pdf-api
sudo chmod 777 /var/pdf-api/uploads
sudo chmod 777 /var/pdf-api/logs
```

#### Port Conflicts

```bash
# Check what's using port 8000
sudo netstat -tlnp | grep :8000

# Kill conflicting process
sudo kill -9 <PID>
```

### Performance Issues

#### Memory Issues

```bash
# Check memory usage
free -h
htop

# Adjust Gunicorn workers
# Edit gunicorn.conf.py and reduce workers
```

#### Disk Space

```bash
# Check disk usage
df -h

# Clean up old files
sudo find /var/pdf-api/uploads -type f -mtime +1 -delete
sudo find /var/log -name "*.log.*" -mtime +7 -delete
```

## 📈 Scaling Considerations

### Vertical Scaling

- Increase instance type (t3.micro → t3.small → t3.medium)
- Increase root volume size
- Enable detailed CloudWatch monitoring

### Horizontal Scaling

- Use Auto Scaling Groups
- Load balancer for multiple instances
- Database for shared state (if needed)

### Performance Optimization

- Use larger instance types for production
- Enable CloudWatch monitoring
- Implement caching strategies
- Use CDN for static assets

## 🔍 Testing Deployment

### Health Check

```bash
curl -f http://your-ec2-ip/health
```

### API Endpoints

```bash
# Test PDF unlock
curl -X POST "http://your-ec2-ip/unlock-pdf" \
  -H "Content-Type: multipart/form-data" \
  -F "pdf_file=@test.pdf"

# Test API documentation
open http://your-ec2-ip/docs
```

### Load Testing

```bash
# Install Apache Bench
sudo yum install -y httpd-tools

# Run load test
ab -n 100 -c 10 http://your-ec2-ip/health
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Amazon Linux Documentation](https://docs.aws.amazon.com/amazonalinux/)

## 🆘 Support

If you encounter issues:

1. Check the logs: `sudo journalctl -u pdf-api -f`
2. Verify service status: `sudo systemctl status pdf-api`
3. Check nginx: `sudo systemctl status nginx`
4. Review this deployment guide
5. Check the build summary: `cat /var/pdf-api/BUILD_SUMMARY.md`

## 📝 Changelog

- **v1.0.0**: Initial deployment scripts and documentation
- Added build scripts for Linux and Windows
- Added Terraform infrastructure as code
- Added Docker deployment options
- Added comprehensive monitoring and logging
- Added security configurations
- Added troubleshooting guide
