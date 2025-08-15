#!/bin/bash

# AWS Lambda Deployment Script for PDF to PowerPoint API

set -e

echo "🚀 Starting Lambda deployment process..."

# Configuration
FUNCTION_NAME="pdf-to-pptx-converter"
REGION="us-east-1"  # Change to your preferred region
RUNTIME="python3.11"
TIMEOUT=300  # 5 minutes
MEMORY_SIZE=3008  # Maximum memory for better performance

# Create deployment directory
echo "📁 Creating deployment package..."
rm -rf lambda-deploy
mkdir -p lambda-deploy

# Copy application code
echo "📋 Copying application code..."
cp -r app lambda-deploy/
cp lambda_handler.py lambda-deploy/
cp requirements-lambda.txt lambda-deploy/requirements.txt

# Install dependencies
echo "📦 Installing dependencies..."
cd lambda-deploy
pip install -r requirements.txt -t .

# Remove unnecessary files to reduce size
echo "🧹 Cleaning up unnecessary files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Create ZIP package
echo "📦 Creating deployment package..."
zip -r ../lambda-deployment.zip . -x "*.git*" "*.DS_Store*" "*__pycache__*"

cd ..

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

echo "☁️ Deploying to AWS Lambda..."

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION > /dev/null 2>&1; then
    echo "🔄 Updating existing function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://lambda-deployment.zip \
        --region $REGION
    
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --timeout $TIMEOUT \
        --memory-size $MEMORY_SIZE \
        --region $REGION
else
    echo "🆕 Creating new function..."
    
    # Create execution role (if not exists)
    ROLE_NAME="lambda-pdf-converter-role"
    ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text 2>/dev/null || echo "")
    
    if [ -z "$ROLE_ARN" ]; then
        echo "🔐 Creating IAM role..."
        
        # Trust policy
        cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
        
        aws iam create-role \
            --role-name $ROLE_NAME \
            --assume-role-policy-document file://trust-policy.json
        
        aws iam attach-role-policy \
            --role-name $ROLE_NAME \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        
        # Wait for role to be ready
        sleep 10
        
        ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
        rm trust-policy.json
    fi
    
    # Create Lambda function
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --role $ROLE_ARN \
        --handler lambda_handler.lambda_handler \
        --zip-file fileb://lambda-deployment.zip \
        --timeout $TIMEOUT \
        --memory-size $MEMORY_SIZE \
        --region $REGION \
        --environment Variables='{LAMBDA_EXECUTION=true}'
fi

echo "🔧 Setting up API Gateway..."

# Create or update API Gateway (you'll need to do this manually or use SAM/CDK)
echo "⚠️  Please create API Gateway manually or use the provided template."

echo "✅ Deployment complete!"
echo "📋 Next steps:"
echo "   1. Create API Gateway REST API"
echo "   2. Set up proxy integration to Lambda function"
echo "   3. Deploy API Gateway stage"
echo "   4. Update API_BASE_URL environment variable"

# Cleanup
rm -rf lambda-deploy
echo "🧹 Cleanup complete!"
