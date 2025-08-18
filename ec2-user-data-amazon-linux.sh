#!/bin/bash

# EC2 User Data Script for PDF Unlock API on Amazon Linux
# This script runs automatically when the EC2 instance starts
# Use this in the "User data" field when launching your Amazon Linux EC2 instance

set -e

# Log all output to a file for debugging
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "🚀 Starting EC2 instance setup for PDF Unlock API on Amazon Linux..."

# Update system packages
echo "Updating system packages..."
yum update -y

# Install required packages
echo "Installing required packages..."
yum install -y \
    python3 \
    python3-pip \
    python3-devel \
    nginx \
    curl \
    wget \
    git \
    unzip \
    supervisor \
    htop \
    firewalld \
    certbot \
    python3-certbot-nginx

# Start and enable firewalld
echo "Configuring firewall..."
systemctl start firewalld
systemctl enable firewalld

# Configure firewall rules
firewall-cmd --permanent --add-service=ssh
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --reload

# Create application user and group
echo "Creating application user and group..."
useradd -r -s /bin/false -d /var/pdf-api pdf-api
mkdir -p /var/pdf-api
chown pdf-api:pdf-api /var/pdf-api

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p /var/pdf-api/uploads
mkdir -p /var/pdf-api/logs
mkdir -p /var/pdf-api/config
chown -R pdf-api:pdf-api /var/pdf-api

# Configure nginx
echo "Configuring nginx..."
cat > /etc/nginx/conf.d/pdf-api.conf << 'EOF'
server {
    listen 80;
    server_name _;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # File upload size limit
    client_max_body_size 50M;

    # Proxy to FastAPI application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static file serving (if needed)
    location /static/ {
        alias /var/pdf-api/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Remove default nginx configuration
rm -f /etc/nginx/conf.d/default.conf

# Test nginx configuration
nginx -t

# Create systemd service file
echo "Creating systemd service file..."
cat > /etc/systemd/system/pdf-api.service << 'EOF'
[Unit]
Description=PDF Unlock API
After=network.target

[Service]
Type=notify
User=pdf-api
Group=pdf-api
WorkingDirectory=/var/pdf-api
Environment=PATH=/var/pdf-api/venv/bin
ExecStart=/var/pdf-api/venv/bin/gunicorn -c gunicorn.conf.py app.main:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create environment file
echo "Creating environment file..."
cat > /var/pdf-api/.env << 'EOF'
# Environment variables for PDF Unlock API
PORT=8000
WORKERS=4
LOG_LEVEL=INFO
CORS_ORIGINS=*
API_KEY_HEADER=X-API-Key
API_KEY=your-secret-api-key-here
FILE_EXPIRY_HOURS=24
MAX_FILE_SIZE=52428800
EOF

# Create a simple health check script
echo "Creating health check script..."
cat > /usr/local/bin/health-check.sh << 'EOF'
#!/bin/bash
# Simple health check script for the PDF API

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "OK"
    exit 0
else
    echo "FAIL"
    exit 1
fi
EOF

chmod +x /usr/local/bin/health-check.sh

# Create log rotation configuration
echo "Configuring log rotation..."
cat > /etc/logrotate.d/pdf-api << 'EOF'
/var/pdf-api/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 pdf-api pdf-api
    postrotate
        systemctl reload pdf-api > /dev/null 2>&1 || true
    endscript
}
EOF

# Create monitoring script
echo "Creating monitoring script..."
cat > /usr/local/bin/monitor-pdf-api.sh << 'EOF'
#!/bin/bash
# Monitoring script for PDF API

LOG_FILE="/var/log/pdf-api-monitor.log"
APP_STATUS=$(systemctl is-active pdf-api)
NGINX_STATUS=$(systemctl is-active nginx)

echo "$(date): PDF API Status: $APP_STATUS, Nginx Status: $NGINX_STATUS" >> "$LOG_FILE"

if [ "$APP_STATUS" != "active" ]; then
    echo "$(date): PDF API is down, attempting restart..." >> "$LOG_FILE"
    systemctl restart pdf-api
fi

if [ "$NGINX_STATUS" != "active" ]; then
    echo "$(date): Nginx is down, attempting restart..." >> "$LOG_FILE"
    systemctl restart nginx
fi
EOF

chmod +x /usr/local/bin/monitor-pdf-api.sh

# Add monitoring to crontab
echo "Adding monitoring to crontab..."
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/monitor-pdf-api.sh") | crontab -

# Create deployment script
echo "Creating deployment script..."
cat > /var/pdf-api/deploy-amazon-linux.sh << 'EOF'
#!/bin/bash

# Deployment script for PDF Unlock API on Amazon Linux
set -e

echo "🚀 Deploying PDF Unlock API..."

# Configuration
APP_NAME="pdf-api"
APP_DIR="/var/$APP_NAME"
SERVICE_USER="$APP_NAME"
SERVICE_GROUP="$APP_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root"
   exit 1
fi

# Create application directory structure
print_status "Creating application directory structure..."
mkdir -p "$APP_DIR/uploads"
mkdir -p "$APP_DIR/logs"
mkdir -p "$APP_DIR/config"

# Set permissions
print_status "Setting permissions..."
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$APP_DIR"
chmod -R 755 "$APP_DIR"
chmod 777 "$APP_DIR/uploads"
chmod 777 "$APP_DIR/logs"

# Create virtual environment
print_status "Creating virtual environment..."
cd "$APP_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Reload systemd and enable service
print_status "Reloading systemd and enabling service..."
systemctl daemon-reload
systemctl enable pdf-api.service

# Start services
print_status "Starting services..."
systemctl start pdf-api.service
systemctl restart nginx

# Check service status
print_status "Checking service status..."
systemctl status pdf-api.service --no-pager
systemctl status nginx --no-pager

print_status "Deployment completed successfully!"
print_status "Application is running on port 8000"
print_status "Nginx is serving on port 80"
print_status "Check logs with: journalctl -u pdf-api -f"
EOF

chmod +x /var/pdf-api/deploy-amazon-linux.sh

# Create a simple status page
echo "Creating status page..."
cat > /var/www/html/status.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>PDF API Status</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .ok { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>PDF Unlock API Status</h1>
    <div id="status"></div>
    <script>
        function checkStatus() {
            fetch('/health')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').innerHTML = 
                        '<div class="status ok">Service is running</div>';
                })
                .catch(error => {
                    document.getElementById('status').innerHTML = 
                        '<div class="status error">Service is down</div>';
                });
        }
        checkStatus();
        setInterval(checkStatus, 30000);
    </script>
</body>
</html>
EOF

# Start nginx
echo "Starting nginx..."
systemctl enable nginx
systemctl start nginx

# Create a simple welcome message
echo "Creating welcome message..."
cat > /var/pdf-api/WELCOME.md << 'EOF'
# PDF Unlock API - Amazon Linux EC2 Instance Setup Complete!

Your Amazon Linux EC2 instance has been configured with the following:

## Services Installed
- Python 3 with pip and venv
- Nginx web server
- Systemd service management
- Firewalld firewall configured
- Log rotation
- Monitoring scripts

## Next Steps
1. Upload your application files to `/var/pdf-api/`
2. Run the deployment script: `sudo /var/pdf-api/deploy-amazon-linux.sh`
3. Your API will be available on port 8000
4. Nginx will proxy requests from port 80 to your application

## Useful Commands
- Check service status: `sudo systemctl status pdf-api`
- View logs: `sudo journalctl -u pdf-api -f`
- Check nginx: `sudo systemctl status nginx`
- Monitor health: `/usr/local/bin/health-check.sh`

## Security Notes
- Firewall is configured to allow SSH, HTTP, HTTPS, and port 8000
- Application runs as non-root user `pdf-api`
- Nginx is configured with security headers

## Monitoring
- Health checks run every 5 minutes
- Logs are rotated daily
- Service auto-restart on failure

## Amazon Linux Specific Notes
- Uses yum package manager instead of apt
- Uses firewalld instead of UFW
- Nginx config is in /etc/nginx/conf.d/
- Python 3 is available by default

Your instance is ready for deployment!
EOF

# Set final permissions
chown -R pdf-api:pdf-api /var/pdf-api

echo "✅ Amazon Linux EC2 instance setup completed successfully!"
echo "📝 Check /var/log/user-data.log for detailed setup information"
echo "📁 Application directory: /var/pdf-api"
echo "🚀 Ready for deployment!"
echo "📖 See /var/pdf-api/WELCOME.md for next steps"

# Optional: Install additional monitoring tools
echo "Installing additional monitoring tools..."
yum install -y \
    htop \
    iotop \
    nethogs \
    iftop

echo "🎉 Setup complete! Your Amazon Linux EC2 instance is ready for the PDF Unlock API."
