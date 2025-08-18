# 🚀 PDF Unlock API - Amazon Linux Deployment

This guide is specifically for deploying the PDF Unlock API on **Amazon Linux 2023** EC2 instances.

## 🎯 Quick Start

### Option 1: Automated Build & Deploy

1. **Build the deployment package:**

   ```bash
   # Use the Amazon Linux specific build script
   ./build-amazon-linux.sh
   ```

2. **Deploy to EC2:**
   ```bash
   # Automated deployment
   ./deploy-ec2.sh
   ```

### Option 2: EC2 User Data (Recommended)

1. **Launch EC2 instance with user data:**

   - Copy the contents of `ec2-user-data-amazon-linux.sh`
   - Paste into the "User data" field when launching your EC2 instance
   - The instance will automatically set up everything

2. **Deploy application:**
   ```bash
   # Upload build files and deploy
   sudo /var/pdf-api/deploy-amazon-linux.sh
   ```

## 🔧 Amazon Linux Specific Features

### Package Management

- **Uses `yum` instead of `apt`**
- **Python 3 is available by default**
- **Nginx configuration goes to `/etc/nginx/conf.d/`**

### Firewall

- **Uses `firewalld` instead of `ufw`**
- **Automatically configured for SSH, HTTP, HTTPS, and port 8000**

### Service Management

- **Systemd is available for service management**
- **Automatic service restart on failure**
- **Log rotation and monitoring scripts**

## 📁 Files for Amazon Linux

### Build Scripts

- **`build-amazon-linux.sh`** - Creates Amazon Linux compatible deployment package
- **`deploy-ec2.sh`** - Automated deployment script

### EC2 Setup

- **`ec2-user-data-amazon-linux.sh`** - EC2 instance initialization script

### Deployment Package

The build script creates a `build/` directory with:

- `deploy-amazon-linux.sh` - Amazon Linux specific deployment script
- `nginx.conf` - Nginx configuration for `/etc/nginx/conf.d/`
- `pdf-api.service` - Systemd service file
- All application files and configurations

## 🚀 Deployment Steps

### 1. Launch EC2 Instance

- **AMI**: Amazon Linux 2023
- **Instance Type**: t3.micro (free tier) or t3.small for production
- **Security Group**: Allow ports 22, 80, 443, 8000
- **User Data**: Paste contents of `ec2-user-data-amazon-linux.sh`

### 2. Wait for Initialization

- Check `/var/log/user-data.log` for progress
- Instance is ready when you see "Setup complete!"

### 3. Deploy Application

```bash
# SSH to your instance
ssh -i your-key.pem ec2-user@your-ec2-ip

# Upload build files
scp -r build/ ec2-user@your-ec2-ip:/tmp/

# Deploy
sudo /tmp/build/deploy-amazon-linux.sh
```

## 🔒 Security Features

- **Non-root user execution** (`pdf-api`)
- **Firewalld configuration** with minimal open ports
- **Security headers** in Nginx
- **Configurable API keys** and CORS
- **Log rotation** and monitoring

## 📊 Monitoring & Maintenance

### Service Status

```bash
# Check services
sudo systemctl status pdf-api nginx

# View logs
sudo journalctl -u pdf-api -f
sudo tail -f /var/log/nginx/error.log
```

### Health Checks

```bash
# Manual health check
curl http://localhost:8000/health

# Automated monitoring
/usr/local/bin/health-check.sh
/usr/local/bin/monitor-pdf-api.sh
```

### Updates

```bash
# System updates
sudo yum update -y

# Restart services if needed
sudo systemctl restart pdf-api nginx
```

## 🆘 Troubleshooting

### Common Issues

1. **Service won't start:**

   ```bash
   sudo journalctl -u pdf-api -f
   sudo systemctl status pdf-api
   ```

2. **Permission issues:**

   ```bash
   sudo chown -R pdf-api:pdf-api /var/pdf-api
   sudo chmod -R 755 /var/pdf-api
   ```

3. **Nginx issues:**
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   ```

### Getting Help

- Check logs: `sudo journalctl -u pdf-api -f`
- Review deployment guide: `cat /var/pdf-api/WELCOME.md`
- Verify service status: `sudo systemctl status pdf-api`

## 🎉 Next Steps

1. **Test your deployment** with the health check endpoint
2. **Configure SSL/HTTPS** for production use
3. **Set up monitoring** and alerting
4. **Implement backups** for your data
5. **Scale horizontally** if needed

## 📚 Additional Resources

- **DEPLOYMENT_GUIDE.md** - Comprehensive deployment guide
- **DEPLOYMENT_SUMMARY.md** - Quick reference overview
- **Amazon Linux Documentation** - System reference
- **AWS EC2 Documentation** - EC2 service reference

---

**Happy Deploying on Amazon Linux! 🚀**

Your PDF Unlock API is now ready for production deployment with enterprise-grade infrastructure optimized for Amazon Linux.
