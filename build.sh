#!/bin/bash

# Build Script for PDF to PowerPoint API using Docker
# Optimized for Amazon Linux (uses yum package manager)

set -e

echo "🔨 Starting Docker build process for EC2 deployment..."

# Configuration
IMAGE_NAME="pdf-to-pptx-api"
IMAGE_TAG="latest"
DOCKERFILE="Dockerfile"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Clean up any existing containers and images
echo "🧹 Cleaning up existing containers and images..."
docker container prune -f > /dev/null 2>&1 || true
docker image prune -f > /dev/null 2>&1 || true

# Remove existing image if it exists
if docker image inspect $IMAGE_NAME:$IMAGE_TAG > /dev/null 2>&1; then
    echo "🗑️  Removing existing image..."
    docker rmi $IMAGE_NAME:$IMAGE_TAG
fi

# Build the Docker image
echo "🏗️  Building Docker image..."
docker build -t $IMAGE_NAME:$IMAGE_TAG -f $DOCKERFILE .

# Verify the build
if docker image inspect $IMAGE_NAME:$IMAGE_TAG > /dev/null 2>&1; then
    echo "✅ Docker image built successfully!"
    echo "📋 Image details:"
    docker images $IMAGE_NAME:$IMAGE_TAG
    
    # Save the image as a tar file for easy transfer to EC2
    echo "💾 Saving image as tar file..."
    docker save $IMAGE_NAME:$IMAGE_TAG -o ${IMAGE_NAME}-${IMAGE_TAG}.tar
    
    echo "🎯 Build complete! Image saved as: ${IMAGE_NAME}-${IMAGE_TAG}.tar"
    echo "📤 You can now transfer this file to your EC2 instance and run deploy-ec2.sh"
else
    echo "❌ Docker build failed!"
    exit 1
fi
