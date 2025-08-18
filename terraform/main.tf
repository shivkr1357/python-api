# Terraform configuration for PDF Unlock API on AWS EC2
# This file sets up the infrastructure needed to run the application

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configure AWS Provider
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "pdf-unlock-api"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Data sources
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

# VPC and Networking
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

resource "aws_subnet" "public" {
  count             = var.az_count
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-subnet-${count.index + 1}"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = var.az_count
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Security Groups
resource "aws_security_group" "pdf_api" {
  name_prefix = "${var.project_name}-pdf-api-"
  vpc_id      = aws_vpc.main.id

  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidrs
    description = "SSH access"
  }

  # HTTP access
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP access"
  }

  # HTTPS access
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS access"
  }

  # Application port (optional, for direct access)
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "PDF API direct access"
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name = "${var.project_name}-pdf-api-sg"
  }
}

# EC2 Instance
resource "aws_instance" "pdf_api" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.pdf_api.id]
  subnet_id              = aws_subnet.public[0].id

  root_block_device {
    volume_size = var.root_volume_size
    volume_type = "gp3"
    encrypted   = true

    tags = {
      Name = "${var.project_name}-root-volume"
    }
  }

  user_data = base64encode(templatefile("${path.module}/../ec2-user-data.sh", {
    project_name = var.project_name
    environment  = var.environment
  }))

  user_data_replace_on_change = true

  tags = {
    Name = "${var.project_name}-pdf-api-instance"
  }

  # Lifecycle policy to prevent replacement on user_data changes
  lifecycle {
    ignore_changes = [user_data]
  }
}

# Elastic IP for the instance
resource "aws_eip" "pdf_api" {
  instance = aws_instance.pdf_api.id
  domain   = "vpc"

  tags = {
    Name = "${var.project_name}-pdf-api-eip"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "pdf_api" {
  name              = "/aws/ec2/${var.project_name}-pdf-api"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.project_name}-pdf-api-logs"
  }
}

# IAM Role for EC2 instance
resource "aws_iam_role" "pdf_api" {
  name = "${var.project_name}-pdf-api-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-pdf-api-role"
  }
}

# IAM Instance Profile
resource "aws_iam_instance_profile" "pdf_api" {
  name = "${var.project_name}-pdf-api-profile"
  role = aws_iam_role.pdf_api.name
}

# Attach IAM role to instance
resource "aws_iam_role_policy_attachment" "pdf_api_ssm" {
  role       = aws_iam_role.pdf_api.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# S3 bucket for backups (optional)
resource "aws_s3_bucket" "backups" {
  count  = var.create_backup_bucket ? 1 : 0
  bucket = "${var.project_name}-backups-${random_string.bucket_suffix[0].result}"

  tags = {
    Name = "${var.project_name}-backups"
  }
}

resource "aws_s3_bucket_versioning" "backups" {
  count  = var.create_backup_bucket ? 1 : 0
  bucket = aws_s3_bucket.backups[0].id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backups" {
  count  = var.create_backup_bucket ? 1 : 0
  bucket = aws_s3_bucket.backups[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "backups" {
  count  = var.create_backup_bucket ? 1 : 0
  bucket = aws_s3_bucket.backups[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Random string for unique bucket names
resource "random_string" "bucket_suffix" {
  count   = var.create_backup_bucket ? 1 : 0
  length  = 8
  special = false
  upper   = false
}

# Outputs
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.pdf_api.id
}

output "public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_eip.pdf_api.public_ip
}

output "public_dns" {
  description = "Public DNS name of the EC2 instance"
  value       = aws_eip.pdf_api.public_dns
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ${var.key_pair_name}.pem ubuntu@${aws_eip.pdf_api.public_ip}"
}

output "api_url" {
  description = "URL to access the PDF API"
  value       = "http://${aws_eip.pdf_api.public_ip}"
}

output "api_docs_url" {
  description = "URL to access the PDF API documentation"
  value       = "http://${aws_eip.pdf_api.public_ip}/docs"
}

output "backup_bucket_name" {
  description = "Name of the S3 backup bucket"
  value       = var.create_backup_bucket ? aws_s3_bucket.backups[0].bucket : null
}
