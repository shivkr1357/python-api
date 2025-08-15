# EC2 Deployment Guide for PDF to PowerPoint API

This guide explains how to deploy your PDF to PowerPoint API on Amazon EC2 using Docker.

## Prerequisites

- Local machine with Docker installed
- EC2 instance running Amazon Linux 2023
- SSH access to your EC2 instance
- Security group configured to allow inbound traffic on port 8000

## Quick Start

### 1. Build the Docker Image (Local Machine)

```bash
# Make sure you're in the project directory
cd /path/to/your/python-api

# Run the build script
./build.sh
```

This will:

- Build a Docker image optimized for Amazon Linux
- Save the image as a tar file (`pdf-to-pptx-api-latest.tar`)
- Clean up any existing containers/images

### 2. Transfer to EC2

Transfer the tar file to your EC2 instance:

```bash
# Using SCP
scp -i your-key.pem pdf-to-pptx-api-latest.tar ec2-user@your-ec2-ip:/home/ec2-user/

# Or using AWS CLI
aws s3 cp pdf-to-pptx-api-latest.tar s3://your-bucket/
# Then download from S3 on EC2
```

### 3. Deploy on EC2

SSH into your EC2 instance and run:

```bash
# Make the script executable
chmod +x deploy-ec2.sh

# Run the deployment script
./deploy-ec2.sh
```

## What the Scripts Do

### build.sh

- Builds Docker image using Amazon Linux 2023 base
- Installs all system dependencies using `dnf` (Amazon Linux 2023 package manager)
- Installs Python dependencies from requirements.txt
- Creates a portable tar file for easy transfer

### deploy-ec2.sh

- Automatically installs Docker and Docker Compose if not present
- Loads the Docker image from the tar file
- Creates necessary output directories
- Runs the container with proper volume mounts
- Sets up health checks and restart policies
- Provides useful management commands

## Configuration

### Port Configuration

- Default port: 8000
- Change in `deploy-ec2.sh` if needed
- Update security group accordingly

### Volume Mounts

- Outputs are stored in `/opt/pdf-api/outputs/`
- PDFs: `/opt/pdf-api/outputs/pdfs/`
- PowerPoint files: `/opt/pdf-api/outputs/pptx/`

### Environment Variables

- `PORT`: Application port (default: 8000)
- `HOST`: Bind address (default: 0.0.0.0)

## Management Commands

```bash
# View logs
sudo docker logs -f pdf-to-pptx-api-container

# Stop the application
sudo docker stop pdf-to-pptx-api-container

# Start the application
sudo docker start pdf-to-pptx-api-container

# Restart the application
sudo docker restart pdf-to-pptx-api-container

# Remove the application
sudo docker rm -f pdf-to-pptx-api-container

# Check container status
sudo docker ps -a
```

## Using Docker Compose

The `deploy-ec2.sh` script also installs Docker Compose. You can use it for easier management:

```bash
# Start with docker-compose
sudo docker-compose up -d

# Stop with docker-compose
sudo docker-compose down

# View logs
sudo docker-compose logs -f

# Restart
sudo docker-compose restart
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Make sure scripts are executable

   ```bash
   chmod +x build.sh deploy-ec2.sh
   ```

2. **Docker Not Running**: The script will install and start Docker automatically

3. **Port Already in Use**: Check if port 8000 is available

   ```bash
   sudo netstat -tlnp | grep :8000
   ```

4. **Container Fails to Start**: Check logs
   ```bash
   sudo docker logs pdf-to-pptx-api-container
   ```

### Health Checks

The application includes health check endpoints:

- Health: `http://your-ec2-ip:8000/health`
- API Docs: `http://your-ec2-ip:8000/docs`

### Security Considerations

- Update security groups to only allow necessary ports
- Consider using HTTPS in production
- Regularly update the base image and dependencies
- Monitor container logs for security issues

## Performance Optimization

- The container uses `--restart unless-stopped` for automatic recovery
- Output directories are mounted as volumes for persistence
- Health checks ensure the application is running properly
- The base image is optimized for Amazon Linux with minimal footprint

## Next Steps

After successful deployment:

1. Test the API endpoints
2. Set up monitoring and logging
3. Configure auto-scaling if needed
4. Set up CI/CD pipeline for automated deployments
5. Configure backup strategies for output files
