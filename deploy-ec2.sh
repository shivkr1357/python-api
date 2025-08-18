#!/bin/bash

# Simple EC2 deployment script for PDF Unlock API
# This script automates the deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Configuration
APP_NAME="pdf-unlock-api"
BUILD_DIR="build"
REMOTE_USER="ubuntu"
REMOTE_DIR="/tmp"

# Check if build directory exists
if [ ! -d "$BUILD_DIR" ]; then
    print_error "Build directory not found. Please run build.sh first."
    exit 1
fi

# Get EC2 IP address
print_header "EC2 Deployment Configuration"
read -p "Enter your EC2 instance IP address: " EC2_IP
read -p "Enter your SSH key path (e.g., ~/.ssh/my-key.pem): " SSH_KEY_PATH

# Validate inputs
if [ -z "$EC2_IP" ]; then
    print_error "EC2 IP address is required"
    exit 1
fi

if [ -z "$SSH_KEY_PATH" ]; then
    print_error "SSH key path is required"
    exit 1
fi

# Expand tilde in SSH key path
SSH_KEY_PATH=$(eval echo $SSH_KEY_PATH)

if [ ! -f "$SSH_KEY_PATH" ]; then
    print_error "SSH key file not found: $SSH_KEY_PATH"
    exit 1
fi

print_status "EC2 IP: $EC2_IP"
print_status "SSH Key: $SSH_KEY_PATH"

# Test SSH connection
print_header "Testing SSH Connection"
print_status "Testing connection to EC2 instance..."
if ! ssh -i "$SSH_KEY_PATH" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$REMOTE_USER@$EC2_IP" "echo 'SSH connection successful'" 2>/dev/null; then
    print_error "Failed to connect to EC2 instance. Please check:"
    echo "  1. EC2 instance is running"
    echo "  2. Security group allows SSH (port 22)"
    echo "  3. SSH key is correct"
    echo "  4. Instance is accessible from your network"
    exit 1
fi

print_status "SSH connection successful!"

# Upload build files
print_header "Uploading Build Files"
print_status "Uploading build directory to EC2..."
if ! scp -i "$SSH_KEY_PATH" -r "$BUILD_DIR" "$REMOTE_USER@$EC2_IP:$REMOTE_DIR/"; then
    print_error "Failed to upload build files"
    exit 1
fi

print_status "Build files uploaded successfully!"

# Deploy application
print_header "Deploying Application"
print_status "Running deployment script on EC2..."
ssh -i "$SSH_KEY_PATH" "$REMOTE_USER@$EC2_IP" << 'EOF'
    echo "🚀 Starting deployment on EC2..."
    
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        echo "❌ This script must be run as root"
        echo "Please run: sudo /tmp/build/deploy.sh"
        exit 1
    fi
    
    # Run deployment script
    cd /tmp/build
    chmod +x deploy.sh
    ./deploy.sh
EOF

if [ $? -eq 0 ]; then
    print_status "Deployment completed successfully!"
else
    print_warning "Deployment script completed with warnings. Please check the output above."
fi

# Test deployment
print_header "Testing Deployment"
print_status "Testing application health..."
sleep 5  # Wait for services to start

if curl -f "http://$EC2_IP/health" > /dev/null 2>&1; then
    print_status "✅ Application is healthy!"
    echo ""
    echo "🎉 Deployment successful! Your PDF Unlock API is now running."
    echo ""
    echo "📱 Access your API:"
    echo "   - Main API: http://$EC2_IP"
    echo "   - API Docs: http://$EC2_IP/docs"
    echo "   - Health Check: http://$EC2_IP/health"
    echo ""
    echo "🔧 Useful commands:"
    echo "   - SSH to instance: ssh -i $SSH_KEY_PATH $REMOTE_USER@$EC2_IP"
    echo "   - Check service status: sudo systemctl status pdf-api"
    echo "   - View logs: sudo journalctl -u pdf-api -f"
    echo "   - Check nginx: sudo systemctl status nginx"
    echo ""
    echo "📊 Monitoring:"
    echo "   - Health check: /usr/local/bin/health-check.sh"
    echo "   - Status page: http://$EC2_IP/status.html"
else
    print_warning "⚠️  Application health check failed. Please check the deployment manually:"
    echo "   SSH to your instance: ssh -i $SSH_KEY_PATH $REMOTE_USER@$EC2_IP"
    echo "   Check service status: sudo systemctl status pdf-api"
    echo "   View logs: sudo journalctl -u pdf-api -f"
fi

# Cleanup
print_header "Cleanup"
print_status "Cleaning up temporary files on EC2..."
ssh -i "$SSH_KEY_PATH" "$REMOTE_USER@$EC2_IP" "sudo rm -rf $REMOTE_DIR/$BUILD_DIR"

print_status "Deployment process completed!"
echo ""
echo "📖 For more information, see:"
echo "   - DEPLOYMENT_GUIDE.md"
echo "   - /var/pdf-api/WELCOME.md (on EC2)"
echo "   - /var/pdf-api/BUILD_SUMMARY.md (on EC2)"
