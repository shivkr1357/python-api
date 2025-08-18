#!/bin/bash

# Build script for PDF Unlock API
# This script prepares the application for deployment

set -e

echo "🚀 Starting build process for PDF Unlock API..."

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

# Create nginx configuration for Amazon Linux
print_status "Creating nginx configuration for Amazon Linux..."
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

# Create deployment script for Docker
print_status "Creating deployment script for Docker..."
cat > "$BUILD_DIR/deploy.sh" << 'EOF'
#!/bin/bash

# Deployment script for PDF Unlock API using Docker on Amazon Linux
set -e

echo "🚀 Deploying PDF Unlock API using Docker..."

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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Installing Docker..."
    # Install Docker on Amazon Linux
    sudo yum update -y
    sudo yum install -y docker
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -a -G docker ec2-user
    print_status "Docker installed and started. Please log out and back in, then run this script again."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed."
fi

# Stop and remove existing containers
print_status "Stopping existing containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Build and start containers
print_status "Building and starting Docker containers..."
docker-compose up -d --build

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 10

# Check container status
print_status "Checking container status..."
docker-compose ps

# Test the application
print_status "Testing application..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "✅ Application is running successfully!"
    print_status "🌐 API is available at: http://localhost:8000"
    print_status "📚 API docs at: http://localhost:8000/docs"
    print_status "🔍 Health check at: http://localhost:8000/health"
else
    print_warning "⚠️  Application might still be starting up. Please wait a moment and check again."
fi

print_status "Deployment completed successfully!"
print_status "Use 'docker-compose logs -f' to view logs"
print_status "Use 'docker-compose down' to stop services"
print_status "Use 'docker-compose up -d' to start services"
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

# Create docker-compose file for production
print_status "Creating docker-compose file for production..."
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
      - CORS_ORIGINS=*
      - API_KEY_HEADER=X-API-Key
      - API_KEY=your-secret-api-key-here
      - FILE_EXPIRY_HOURS=24
      - MAX_FILE_SIZE=52428800
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - pdf-api-network

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
    networks:
      - pdf-api-network

networks:
  pdf-api-network:
    driver: bridge

volumes:
  uploads:
  logs:
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
    "platform": "ubuntu",
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
      "sites_enabled": "pdf-api"
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
chmod +x "$BUILD_DIR/deploy.sh"

# Create build summary for Docker deployment
print_status "Creating build summary for Docker deployment..."
cat > "$BUILD_DIR/BUILD_SUMMARY.md" << 'EOF'
# Build Summary - Docker Deployment

This build contains the following files for deploying PDF Unlock API using Docker on Amazon Linux:

## Core Application Files
- `app/` - Application source code
- `requirements.txt` - Python dependencies
- `start_server.py` - Development server script
- `gunicorn.conf.py` - Production server configuration

## Deployment Files
- `deploy.sh` - Docker deployment script
- `nginx.conf` - Nginx reverse proxy configuration
- `deploy-config.json` - Deployment configuration

## Container Files
- `Dockerfile` - Docker container definition
- `docker-compose.yml` - Multi-container deployment
- `.dockerignore` - Docker build exclusions
- `.env.template` - Environment variables template

## Next Steps
1. Copy the build directory to your Amazon Linux EC2 instance
2. Run `./deploy.sh` to deploy using Docker
3. Or manually: `docker-compose up -d`

## Docker Commands
- Start: `docker-compose up -d`
- Stop: `docker-compose down`
- Logs: `docker-compose logs -f`
- Status: `docker-compose ps`
- Rebuild: `docker-compose up -d --build`

## Application Access
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Nginx: http://localhost:80 (proxies to API)

## Environment Variables
- Edit `.env.template` and rename to `.env` for custom configuration
- Or modify `docker-compose.yml` environment section
EOF

print_status "Build completed successfully!"
print_status "Build directory: $BUILD_DIR"
print_status "Next steps:"
echo "  1. Copy the build directory to your Amazon Linux EC2 instance"
echo "  2. Run: ./deploy.sh (Docker deployment)"
echo "  3. Or manually: docker-compose up -d"
echo ""
print_status "Build summary created: $BUILD_DIR/BUILD_SUMMARY.md"
