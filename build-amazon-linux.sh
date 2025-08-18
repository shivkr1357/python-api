#!/bin/bash

# Build script for PDF Unlock API (Amazon Linux version)
# This script prepares the application for deployment on Amazon Linux

set -e

echo "🚀 Starting build process for PDF Unlock API (Amazon Linux)..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Linux/Unix
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    print_error "This script is designed for Linux/Unix systems. Please use build.bat for Windows."
    exit 1
fi

# Create build directory
BUILD_DIR="build"
print_status "Creating build directory: $BUILD_DIR"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copy application files
print_status "Copying application files..."
cp -r app/ "$BUILD_DIR/"
cp requirements_simple.txt "$BUILD_DIR/requirements.txt"
cp start_server.py "$BUILD_DIR/"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p "$BUILD_DIR/uploads"
mkdir -p "$BUILD_DIR/logs"
mkdir -p "$BUILD_DIR/config"

# Create production configuration
print_status "Creating production configuration..."
cat > "$BUILD_DIR/config/production.py" << 'EOF'
# Production configuration
import os

# Server settings
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 8000))
WORKERS = int(os.getenv("WORKERS", 4))

# File settings
UPLOAD_DIR = "/var/pdf-api/uploads"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
FILE_EXPIRY_HOURS = 24

# Security settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")
API_KEY = os.getenv("API_KEY", "")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "/var/pdf-api/logs/app.log"

# Database (if needed in future)
DATABASE_URL = os.getenv("DATABASE_URL", "")
EOF

# Create gunicorn configuration
print_status "Creating Gunicorn configuration..."
cat > "$BUILD_DIR/gunicorn.conf.py" << 'EOF'
# Gunicorn configuration for production
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', 8000)}"
backlog = 2048

# Worker processes
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/pdf-api/logs/access.log"
errorlog = "/var/pdf-api/logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "pdf-api"

# Server mechanics
daemon = False
pidfile = "/var/pdf-api/pdf-api.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment and configure if using HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
EOF

# Create systemd service file
print_status "Creating systemd service file..."
cat > "$BUILD_DIR/pdf-api.service" << 'EOF'
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

# Create nginx configuration
print_status "Creating nginx configuration..."
cat > "$BUILD_DIR/nginx.conf" << 'EOF'
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

# Create Amazon Linux deployment script
print_status "Creating Amazon Linux deployment script..."
cat > "$BUILD_DIR/deploy-amazon-linux.sh" << 'EOF'
#!/bin/bash

# Deployment script for PDF Unlock API on Amazon Linux
set -e

echo "🚀 Deploying PDF Unlock API on Amazon Linux..."

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

# Update system packages
print_status "Updating system packages..."
yum update -y

# Install required packages
print_status "Installing required packages..."
yum install -y python3 python3-pip python3-devel nginx curl wget git

# Create service user and group
print_status "Creating service user and group..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/false -d "$APP_DIR" "$SERVICE_USER"
    print_status "Created user: $SERVICE_USER"
else
    print_status "User $SERVICE_USER already exists"
fi

# Create application directory
print_status "Creating application directory..."
mkdir -p "$APP_DIR"
mkdir -p "$APP_DIR/uploads"
mkdir -p "$APP_DIR/logs"
mkdir -p "$APP_DIR/config"

# Copy application files
print_status "Copying application files..."
cp -r app/ "$APP_DIR/"
cp requirements.txt "$APP_DIR/"
cp start_server.py "$APP_DIR/"
cp gunicorn.conf.py "$APP_DIR/"
cp -r config/ "$APP_DIR/"

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

# Install systemd service
print_status "Installing systemd service..."
cp pdf-api.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable pdf-api.service

# Install nginx configuration
print_status "Installing nginx configuration..."
cp nginx.conf /etc/nginx/conf.d/pdf-api.conf
rm -f /etc/nginx/conf.d/default.conf

# Test nginx configuration
print_status "Testing nginx configuration..."
nginx -t

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

# Create Dockerfile
print_status "Creating Dockerfile..."
cat > "$BUILD_DIR/Dockerfile" << 'EOF'
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libffi-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p uploads logs

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]
EOF

# Create docker-compose file
print_status "Creating docker-compose file..."
cat > "$BUILD_DIR/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  pdf-api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    environment:
      - PORT=8000
      - WORKERS=4
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./uploads:/var/pdf-api/uploads:ro
    depends_on:
      - pdf-api
    restart: unless-stopped
EOF

# Create .dockerignore
print_status "Creating .dockerignore..."
cat > "$BUILD_DIR/.dockerignore" << 'EOF'
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
build/
dist/
*.egg-info/
.venv
venv/
.env
.venv
ENV/
env/
.idea/
.vscode/
*.swp
*.swo
*~
EOF

# Create environment file template
print_status "Creating environment file template..."
cat > "$BUILD_DIR/.env.template" << 'EOF'
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

# Create deployment configuration
print_status "Creating deployment configuration..."
cat > "$BUILD_DIR/deploy-config.json" << 'EOF'
{
  "app_name": "pdf-api",
  "version": "1.0.0",
  "deployment": {
    "type": "ec2",
    "platform": "amazon-linux",
    "python_version": "3.11",
    "port": 8000,
    "nginx_port": 80
  },
  "services": {
    "app": {
      "user": "pdf-api",
      "group": "pdf-api",
      "directory": "/var/pdf-api",
      "service_file": "pdf-api.service"
    },
    "nginx": {
      "config_file": "nginx.conf",
      "conf_dir": "/etc/nginx/conf.d"
    }
  },
  "directories": {
    "uploads": "/var/pdf-api/uploads",
    "logs": "/var/pdf-api/logs",
    "config": "/var/pdf-api/config"
  },
  "permissions": {
    "app_dir": "755",
    "uploads": "777",
    "logs": "777"
  }
}
EOF

# Make scripts executable
print_status "Making scripts executable..."
chmod +x "$BUILD_DIR/deploy-amazon-linux.sh"

# Create build summary
print_status "Creating build summary..."
cat > "$BUILD_DIR/BUILD_SUMMARY.md" << 'EOF'
# Build Summary (Amazon Linux)

This build contains the following files for deploying PDF Unlock API to Amazon Linux EC2:

## Core Application Files
- `app/` - Application source code
- `requirements.txt` - Python dependencies
- `start_server.py` - Development server script
- `gunicorn.conf.py` - Production server configuration

## Deployment Files
- `deploy-amazon-linux.sh` - Main deployment script for Amazon Linux
- `pdf-api.service` - Systemd service file
- `nginx.conf` - Nginx reverse proxy configuration
- `deploy-config.json` - Deployment configuration

## Container Files
- `Dockerfile` - Docker container definition
- `docker-compose.yml` - Multi-container deployment
- `.dockerignore` - Docker build exclusions
- `.env.template` - Environment variables template

## Next Steps
1. Copy the build directory to your Amazon Linux EC2 instance
2. Run `sudo ./deploy-amazon-linux.sh` to deploy the application
3. Or use Docker: `docker-compose up -d`

## Service Management
- Start: `sudo systemctl start pdf-api`
- Stop: `sudo systemctl stop pdf-api`
- Status: `sudo systemctl status pdf-api`
- Logs: `sudo journalctl -u pdf-api -f`

## Nginx Management
- Start: `sudo systemctl start nginx`
- Reload: `sudo systemctl reload nginx`
- Status: `sudo systemctl status nginx`

## Amazon Linux Specific Notes
- Uses yum package manager instead of apt
- Nginx config goes to /etc/nginx/conf.d/ instead of sites-available
- Python 3 is available by default
- Systemd is available for service management
EOF

print_status "Build completed successfully!"
print_status "Build directory: $BUILD_DIR"
print_status "Next steps:"
echo "  1. Copy the build directory to your Amazon Linux EC2 instance"
echo "  2. Run: sudo ./deploy-amazon-linux.sh"
echo "  3. Or use Docker: docker-compose up -d"
echo ""
print_status "Build summary created: $BUILD_DIR/BUILD_SUMMARY.md"
