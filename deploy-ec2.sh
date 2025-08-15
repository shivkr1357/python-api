#!/bin/bash

# EC2 Deployment Script for PDF to PowerPoint API using Docker
# Optimized for Amazon Linux (uses yum package manager)

set -e

echo "🚀 Starting EC2 deployment process..."

# Configuration
IMAGE_NAME="pdf-to-pptx-api"
IMAGE_TAG="latest"
CONTAINER_NAME="pdf-to-pptx-api-container"
PORT=8000
IMAGE_TAR="${IMAGE_NAME}-${IMAGE_TAG}.tar"

# Check if running on Amazon Linux
if ! grep -q "Amazon Linux" /etc/os-release 2>/dev/null; then
    echo "⚠️  Warning: This script is optimized for Amazon Linux. You're running on:"
    cat /etc/os-release | grep PRETTY_NAME || echo "Unknown OS"
    echo "Continuing anyway..."
fi

# Function to install Docker if not present
install_docker() {
    echo "🐳 Installing Docker..."
    
    # Update system packages
    sudo yum update -y
    
    # Install Docker
    sudo yum install -y docker
    
    # Start and enable Docker service
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # Add current user to docker group
    sudo usermod -a -G docker $USER
    
    echo "✅ Docker installed successfully!"
    echo "🔄 Please log out and log back in for group changes to take effect, or run: newgrp docker"
}

# Function to install Docker Compose if not present
install_docker_compose() {
    echo "🐙 Installing Docker Compose..."
    
    # Install Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    # Create symlink for easier access
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    echo "✅ Docker Compose installed successfully!"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "🐳 Docker not found. Installing..."
    install_docker
    exit 0  # Exit to allow user to log back in
fi

# Check if Docker is running
if ! sudo systemctl is-active --quiet docker; then
    echo "🚀 Starting Docker service..."
    sudo systemctl start docker
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "🐙 Docker Compose not found. Installing..."
    install_docker_compose
fi

# Check if image tar file exists
if [ ! -f "$IMAGE_TAR" ]; then
    echo "❌ Image tar file not found: $IMAGE_TAR"
    echo "📋 Please ensure you have run build.sh first and transferred the tar file to this EC2 instance."
    exit 1
fi

# Load the Docker image
echo "📥 Loading Docker image from tar file..."
sudo docker load -i "$IMAGE_TAR"

# Stop and remove existing container if it exists
if sudo docker ps -a --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
    echo "🔄 Stopping existing container..."
    sudo docker stop "$CONTAINER_NAME" || true
    sudo docker rm "$CONTAINER_NAME" || true
fi

# Create output directories
echo "📁 Creating output directories..."
sudo mkdir -p /opt/pdf-api/outputs/pdfs
sudo mkdir -p /opt/pdf-api/outputs/pptx
sudo chown -R $USER:$USER /opt/pdf-api/outputs

# Run the container
echo "🚀 Starting the application container..."
sudo docker run -d \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    -p "$PORT:$PORT" \
    -v /opt/pdf-api/outputs:/app/outputs \
    -e PORT="$PORT" \
    -e HOST="0.0.0.0" \
    "$IMAGE_NAME:$IMAGE_TAG"

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 10

# Check container status
if sudo docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$CONTAINER_NAME"; then
    echo "✅ Container started successfully!"
    echo "📋 Container status:"
    sudo docker ps --filter "name=$CONTAINER_NAME"
    
    echo "🌐 Application is running on:"
    echo "   Local: http://localhost:$PORT"
    echo "   Network: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'YOUR_EC2_PUBLIC_IP'):$PORT"
    
    echo "📚 API Documentation:"
    echo "   Swagger UI: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'YOUR_EC2_PUBLIC_IP'):$PORT/docs"
    
    echo "🔍 Health Check:"
    echo "   Health endpoint: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'YOUR_EC2_PUBLIC_IP'):$PORT/health"
    
    # Show logs
    echo "📜 Recent container logs:"
    sudo docker logs --tail 20 "$CONTAINER_NAME"
    
else
    echo "❌ Container failed to start!"
    echo "📜 Container logs:"
    sudo docker logs "$CONTAINER_NAME" || true
    exit 1
fi

echo ""
echo "🎯 Deployment complete!"
echo "📋 Useful commands:"
echo "   View logs: sudo docker logs -f $CONTAINER_NAME"
echo "   Stop app: sudo docker stop $CONTAINER_NAME"
echo "   Start app: sudo docker start $CONTAINER_NAME"
echo "   Restart app: sudo docker restart $CONTAINER_NAME"
echo "   Remove app: sudo docker rm -f $CONTAINER_NAME"
