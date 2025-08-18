@echo off
REM Build script for PDF Unlock API (Windows version)
REM This script prepares the application for deployment

echo 🚀 Starting build process for PDF Unlock API...

REM Create build directory
set BUILD_DIR=build
echo [INFO] Creating build directory: %BUILD_DIR%
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
mkdir "%BUILD_DIR%"

REM Copy application files
echo [INFO] Copying application files...
xcopy /E /I app "%BUILD_DIR%\app"
copy requirements_simple.txt "%BUILD_DIR%\requirements.txt"
copy start_server.py "%BUILD_DIR%\"

REM Create necessary directories
echo [INFO] Creating necessary directories...
mkdir "%BUILD_DIR%\uploads"
mkdir "%BUILD_DIR%\logs"
mkdir "%BUILD_DIR%\config"

REM Create production configuration
echo [INFO] Creating production configuration...
(
echo # Production configuration
echo import os
echo.
echo # Server settings
echo HOST = "0.0.0.0"
echo PORT = int^(os.getenv^("PORT", 8000^)^)
echo WORKERS = int^(os.getenv^("WORKERS", 4^)^)
echo.
echo # File settings
echo UPLOAD_DIR = "/var/pdf-api/uploads"
echo MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
echo FILE_EXPIRY_HOURS = 24
echo.
echo # Security settings
echo CORS_ORIGINS = os.getenv^("CORS_ORIGINS", "*"^).split^(","^)
echo API_KEY_HEADER = os.getenv^("API_KEY_HEADER", "X-API-Key"^)
echo API_KEY = os.getenv^("API_KEY", ""^)
echo.
echo # Logging
echo LOG_LEVEL = os.getenv^("LOG_LEVEL", "INFO"^)
echo LOG_FILE = "/var/pdf-api/logs/app.log"
echo.
echo # Database ^(if needed in future^)
echo DATABASE_URL = os.getenv^("DATABASE_URL", ""^)
) > "%BUILD_DIR%\config\production.py"

REM Create gunicorn configuration
echo [INFO] Creating Gunicorn configuration...
(
echo # Gunicorn configuration for production
echo import multiprocessing
echo import os
echo.
echo # Server socket
echo bind = f"0.0.0.0:{os.getenv^('PORT', 8000^)}"
echo backlog = 2048
echo.
echo # Worker processes
echo workers = int^(os.getenv^('WORKERS', multiprocessing.cpu_count^(^) * 2 + 1^)^)
echo worker_class = "uvicorn.workers.UvicornWorker"
echo worker_connections = 1000
echo max_requests = 1000
echo max_requests_jitter = 50
echo timeout = 30
echo keepalive = 2
echo.
echo # Restart workers after this many requests, to help prevent memory leaks
echo max_requests = 1000
echo max_requests_jitter = 50
echo.
echo # Logging
echo accesslog = "/var/pdf-api/logs/access.log"
echo errorlog = "/var/pdf-api/logs/error.log"
echo loglevel = "info"
echo access_log_format = '%%^(h^)s %%^(l^)s %%^(u^)s %%^(t^)s "%%^(r^)s" %%^(s^)s %%^(b^)s "%%^(f^)s" "%%^(a^)s"'
echo.
echo # Process naming
echo proc_name = "pdf-api"
echo.
echo # Server mechanics
echo daemon = False
echo pidfile = "/var/pdf-api/pdf-api.pid"
echo user = None
echo group = None
echo tmp_upload_dir = None
echo.
echo # SSL ^(uncomment and configure if using HTTPS^)
echo # keyfile = "/path/to/keyfile"
echo # certfile = "/path/to/certfile"
) > "%BUILD_DIR%\gunicorn.conf.py"

REM Create systemd service file
echo [INFO] Creating systemd service file...
(
echo [Unit]
echo Description=PDF Unlock API
echo After=network.target
echo.
echo [Service]
echo Type=notify
echo User=pdf-api
echo Group=pdf-api
echo WorkingDirectory=/var/pdf-api
echo Environment=PATH=/var/pdf-api/venv/bin
echo ExecStart=/var/pdf-api/venv/bin/gunicorn -c gunicorn.conf.py app.main:app
echo ExecReload=/bin/kill -s HUP $MAINPID
echo KillMode=mixed
echo TimeoutStopSec=5
echo PrivateTmp=true
echo Restart=always
echo RestartSec=10
echo.
echo [Install]
echo WantedBy=multi-user.target
) > "%BUILD_DIR%\pdf-api.service"

REM Create nginx configuration
echo [INFO] Creating nginx configuration...
(
echo server {
echo     listen 80;
echo     server_name _;
echo.
echo     # Security headers
echo     add_header X-Frame-Options "SAMEORIGIN" always;
echo     add_header X-XSS-Protection "1; mode=block" always;
echo     add_header X-Content-Type-Options "nosniff" always;
echo     add_header Referrer-Policy "no-referrer-when-downgrade" always;
echo     add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
echo.
echo     # File upload size limit
echo     client_max_body_size 50M;
echo.
echo     # Proxy to FastAPI application
echo     location / {
echo         proxy_pass http://127.0.0.1:8000;
echo         proxy_set_header Host $host;
echo         proxy_set_header X-Real-IP $remote_addr;
echo         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
echo         proxy_set_header X-Forwarded-Proto $scheme;
echo         
echo         # Timeouts
echo         proxy_connect_timeout 60s;
echo         proxy_send_timeout 60s;
echo         proxy_read_timeout 60s;
echo     }
echo.
echo     # Static file serving ^(if needed^)
echo     location /static/ {
echo         alias /var/pdf-api/static/;
echo         expires 1y;
echo         add_header Cache-Control "public, immutable";
echo     }
echo }
) > "%BUILD_DIR%\nginx.conf"

REM Create deployment script
echo [INFO] Creating deployment script...
(
echo #!/bin/bash
echo.
echo # Deployment script for PDF Unlock API on EC2
echo set -e
echo.
echo echo "🚀 Deploying PDF Unlock API..."
echo.
echo # Configuration
echo APP_NAME="pdf-api"
echo APP_DIR="/var/$APP_NAME"
echo SERVICE_USER="$APP_NAME"
echo SERVICE_GROUP="$APP_NAME"
echo.
echo # Colors for output
echo RED='\033[0;31m'
echo GREEN='\033[0;32m'
echo YELLOW='\033[1;33m'
echo NC='\033[0m'
echo.
echo print_status^(^) {
echo     echo -e "${GREEN}[INFO]${NC} $1"
echo }
echo.
echo print_warning^(^) {
echo     echo -e "${YELLOW}[WARNING]${NC} $1"
echo }
echo.
echo print_error^(^) {
echo     echo -e "${RED}[ERROR]${NC} $1"
echo }
echo.
echo # Check if running as root
echo if [[ $EUID -ne 0 ]]; then
echo    print_error "This script must be run as root"
echo    exit 1
echo fi
echo.
echo # Create service user and group
echo print_status "Creating service user and group..."
echo if ! id "$SERVICE_USER" &^>/dev/null; then
echo     useradd -r -s /bin/false -d "$APP_DIR" "$SERVICE_USER"
echo     print_status "Created user: $SERVICE_USER"
echo else
echo     print_status "User $SERVICE_USER already exists"
echo fi
echo.
echo # Create application directory
echo print_status "Creating application directory..."
echo mkdir -p "$APP_DIR"
echo mkdir -p "$APP_DIR/uploads"
echo mkdir -p "$APP_DIR/logs"
echo mkdir -p "$APP_DIR/config"
echo.
echo # Copy application files
echo print_status "Copying application files..."
echo cp -r app/ "$APP_DIR/"
echo cp requirements.txt "$APP_DIR/"
echo cp start_server.py "$APP_DIR/"
echo cp gunicorn.conf.py "$APP_DIR/"
echo cp -r config/ "$APP_DIR/"
echo.
echo # Set permissions
echo print_status "Setting permissions..."
echo chown -R "$SERVICE_USER:$SERVICE_GROUP" "$APP_DIR"
echo chmod -R 755 "$APP_DIR"
echo chmod 777 "$APP_DIR/uploads"
echo chmod 777 "$APP_DIR/logs"
echo.
echo # Create virtual environment
echo print_status "Creating virtual environment..."
echo cd "$APP_DIR"
echo python3 -m venv venv
echo source venv/bin/activate
echo pip install --upgrade pip
echo pip install -r requirements.txt
echo pip install gunicorn
echo.
echo # Install systemd service
echo print_status "Installing systemd service..."
echo cp pdf-api.service /etc/systemd/system/
echo systemctl daemon-reload
echo systemctl enable pdf-api.service
echo.
echo # Install nginx configuration
echo print_status "Installing nginx configuration..."
echo cp nginx.conf /etc/nginx/sites-available/pdf-api
echo ln -sf /etc/nginx/sites-available/pdf-api /etc/nginx/sites-enabled/
echo rm -f /etc/nginx/sites-enabled/default
echo.
echo # Test nginx configuration
echo print_status "Testing nginx configuration..."
echo nginx -t
echo.
echo # Start services
echo print_status "Starting services..."
echo systemctl start pdf-api.service
echo systemctl restart nginx
echo.
echo # Check service status
echo print_status "Checking service status..."
echo systemctl status pdf-api.service --no-pager
echo systemctl status nginx --no-pager
echo.
echo print_status "Deployment completed successfully!"
echo print_status "Application is running on port 8000"
echo print_status "Nginx is serving on port 80"
echo print_status "Check logs with: journalctl -u pdf-api -f"
) > "%BUILD_DIR%\deploy.sh"

REM Create Dockerfile
echo [INFO] Creating Dockerfile...
(
echo FROM python:3.11-slim
echo.
echo # Set environment variables
echo ENV PYTHONDONTWRITEBYTECODE=1
echo ENV PYTHONUNBUFFERED=1
echo ENV PORT=8000
echo.
echo # Set work directory
echo WORKDIR /app
echo.
echo # Install system dependencies
echo RUN apt-get update \
echo     ^&^& apt-get install -y --no-install-recommends \
echo         gcc \
echo         g++ \
echo         libffi-dev \
echo         libssl-dev \
echo     ^&^& rm -rf /var/lib/apt/lists/*
echo.
echo # Install Python dependencies
echo COPY requirements.txt .
echo RUN pip install --no-cache-dir -r requirements.txt
echo RUN pip install gunicorn
echo.
echo # Copy project
echo COPY . .
echo.
echo # Create necessary directories
echo RUN mkdir -p uploads logs
echo.
echo # Create non-root user
echo RUN useradd -m -u 1000 appuser ^&^& chown -R appuser:appuser /app
echo USER appuser
echo.
echo # Expose port
echo EXPOSE 8000
echo.
echo # Health check
echo HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
echo     CMD curl -f http://localhost:8000/health ^|^| exit 1
echo.
echo # Run the application
echo CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]
) > "%BUILD_DIR%\Dockerfile"

REM Create docker-compose file
echo [INFO] Creating docker-compose file...
(
echo version: '3.8'
echo.
echo services:
echo   pdf-api:
echo     build: .
echo     ports:
echo       - "8000:8000"
echo     volumes:
echo       - ./uploads:/app/uploads
echo       - ./logs:/app/logs
echo     environment:
echo       - PORT=8000
echo       - WORKERS=4
echo       - LOG_LEVEL=INFO
echo     restart: unless-stopped
echo     healthcheck:
echo       test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
echo       interval: 30s
echo       timeout: 10s
echo       retries: 3
echo       start_period: 40s
echo.
echo   nginx:
echo     image: nginx:alpine
echo     ports:
echo       - "80:80"
echo     volumes:
echo       - ./nginx.conf:/etc/nginx/conf.d/default.conf
echo       - ./uploads:/var/pdf-api/uploads:ro
echo     depends_on:
echo       - pdf-api
echo     restart: unless-stopped
) > "%BUILD_DIR%\docker-compose.yml"

REM Create .dockerignore
echo [INFO] Creating .dockerignore...
(
echo __pycache__
echo *.pyc
echo *.pyo
echo *.pyd
echo .Python
echo env
echo pip-log.txt
echo pip-delete-this-directory.txt
echo .tox
echo .coverage
echo .coverage.*
echo .cache
echo nosetests.xml
echo coverage.xml
echo *.cover
echo *.log
echo .git
echo .mypy_cache
echo .pytest_cache
echo .hypothesis
echo build/
echo dist/
echo *.egg-info/
echo .venv
echo venv/
echo .env
echo .venv
echo ENV/
echo env/
echo .idea/
echo .vscode/
echo *.swp
echo *.swo
echo *~
) > "%BUILD_DIR%\.dockerignore"

REM Create environment file template
echo [INFO] Creating environment file template...
(
echo # Environment variables for PDF Unlock API
echo PORT=8000
echo WORKERS=4
echo LOG_LEVEL=INFO
echo CORS_ORIGINS=*
echo API_KEY_HEADER=X-API-Key
echo API_KEY=your-secret-api-key-here
echo FILE_EXPIRY_HOURS=24
echo MAX_FILE_SIZE=52428800
) > "%BUILD_DIR%\.env.template"

REM Create deployment configuration
echo [INFO] Creating deployment configuration...
(
echo {
echo   "app_name": "pdf-api",
echo   "version": "1.0.0",
echo   "deployment": {
echo     "type": "ec2",
echo     "platform": "ubuntu",
echo     "python_version": "3.11",
echo     "port": 8000,
echo     "nginx_port": 80
echo   },
echo   "services": {
echo     "app": {
echo       "user": "pdf-api",
echo       "group": "pdf-api",
echo       "directory": "/var/pdf-api",
echo       "service_file": "pdf-api.service"
echo     },
echo     "nginx": {
echo       "config_file": "nginx.conf",
echo       "sites_enabled": "pdf-api"
echo     }
echo   },
echo   "directories": {
echo     "uploads": "/var/pdf-api/uploads",
echo     "logs": "/var/pdf-api/logs",
echo     "config": "/var/pdf-api/config"
echo   },
echo   "permissions": {
echo     "app_dir": "755",
echo     "uploads": "777",
echo     "logs": "777"
echo   }
echo }
) > "%BUILD_DIR%\deploy-config.json"

REM Create build summary
echo [INFO] Creating build summary...
(
echo # Build Summary
echo.
echo This build contains the following files for deploying PDF Unlock API to EC2:
echo.
echo ## Core Application Files
echo - `app/` - Application source code
echo - `requirements.txt` - Python dependencies
echo - `start_server.py` - Development server script
echo - `gunicorn.conf.py` - Production server configuration
echo.
echo ## Deployment Files
echo - `deploy.sh` - Main deployment script
echo - `pdf-api.service` - Systemd service file
echo - `nginx.conf` - Nginx reverse proxy configuration
echo - `deploy-config.json` - Deployment configuration
echo.
echo ## Container Files
echo - `Dockerfile` - Docker container definition
echo - `docker-compose.yml` - Multi-container deployment
echo - `.dockerignore` - Docker build exclusions
echo - `.env.template` - Environment variables template
echo.
echo ## Next Steps
echo 1. Copy the build directory to your EC2 instance
echo 2. Run `sudo ./deploy.sh` to deploy the application
echo 3. Or use Docker: `docker-compose up -d`
echo.
echo ## Service Management
echo - Start: `sudo systemctl start pdf-api`
echo - Stop: `sudo systemctl stop pdf-api`
echo - Status: `sudo systemctl status pdf-api`
echo - Logs: `sudo journalctl -u pdf-api -f`
echo.
echo ## Nginx Management
echo - Start: `sudo systemctl start nginx`
echo - Reload: `sudo systemctl reload nginx`
echo - Status: `sudo systemctl status nginx`
) > "%BUILD_DIR%\BUILD_SUMMARY.md"

echo [INFO] Build completed successfully!
echo [INFO] Build directory: %BUILD_DIR%
echo [INFO] Next steps:
echo   1. Copy the build directory to your EC2 instance
echo   2. Run: sudo ./deploy.sh
echo   3. Or use Docker: docker-compose up -d
echo.
echo [INFO] Build summary created: %BUILD_DIR%\BUILD_SUMMARY.md
pause
