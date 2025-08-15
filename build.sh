#!/bin/bash

# Build Script for PDF to PowerPoint API using Docker
# Optimized for Amazon Linux 2023 (uses dnf package manager)

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
if docker build -t $IMAGE_NAME:$IMAGE_TAG -f $DOCKERFILE .; then
    echo "✅ Docker image built successfully!"
    echo "📋 Image details:"
    docker images $IMAGE_NAME:$IMAGE_TAG
    
    # Save the image as a tar file for easy transfer to EC2
    echo "💾 Saving image as tar file..."
    if docker save $IMAGE_NAME:$IMAGE_TAG -o ${IMAGE_NAME}-${IMAGE_TAG}.tar; then
        echo "🎯 Build complete! Image saved as: ${IMAGE_NAME}-${IMAGE_TAG}.tar"
        echo "📤 You can now transfer this file to your EC2 instance and run deploy-ec2.sh"
        
        # Show file size for transfer planning
        FILE_SIZE=$(du -h ${IMAGE_NAME}-${IMAGE_TAG}.tar | cut -f1)
        echo "📏 File size: $FILE_SIZE"
        
        # Verify the tar file
        echo "🔍 Verifying tar file..."
        if tar -tf ${IMAGE_NAME}-${IMAGE_TAG}.tar > /dev/null 2>&1; then
            echo "✅ Tar file verification successful!"
            
            # Show transfer instructions
            echo ""
            echo "🚀 Ready for deployment!"
            echo "📋 Next steps:"
            echo "   1. Transfer the tar file to your EC2 instance:"
            echo "      scp -i your-key.pem ${IMAGE_NAME}-${IMAGE_TAG}.tar ec2-user@your-ec2-ip:/home/ec2-user/"
            echo "   2. SSH into your EC2 instance"
            echo "   3. Run: chmod +x deploy-ec2.sh && ./deploy-ec2.sh"
            echo ""
            echo "💡 Tip: The tar file is quite large. Consider using S3 for transfer:"
            echo "      aws s3 cp ${IMAGE_NAME}-${IMAGE_TAG}.tar s3://your-bucket/"
            echo "      # Then on EC2: aws s3 cp s3://your-bucket/${IMAGE_NAME}-${IMAGE_TAG}.tar ."
            
        else
            echo "❌ Tar file verification failed!"
            exit 1
        fi
    else
        echo "❌ Failed to save Docker image to tar file!"
        exit 1
    fi
else
    echo "❌ Docker build failed!"
    exit 1
fi
