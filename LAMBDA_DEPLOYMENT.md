# 🚀 AWS Lambda Deployment Guide

## Prerequisites

### 1. Install AWS CLI
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Configure AWS CLI
aws configure
```

### 2. Install SAM CLI (Recommended)
```bash
# Install SAM CLI
brew install aws-sam-cli
```

## Deployment Options

### Option 1: Using SAM (Recommended)

#### Step 1: Build and Deploy
```bash
# Build the application
sam build

# Deploy (first time)
sam deploy --guided

# Deploy subsequent updates
sam deploy
```

#### Step 2: Get API URL
```bash
# Get the API Gateway URL
sam list stack-outputs --stack-name pdf-to-pptx-converter
```

### Option 2: Using Deployment Script

#### Step 1: Make Script Executable
```bash
chmod +x deploy.sh
```

#### Step 2: Run Deployment
```bash
./deploy.sh
```

#### Step 3: Setup API Gateway Manually
1. Go to AWS Console → API Gateway
2. Create REST API
3. Create resource `{proxy+}`
4. Create method `ANY` with Lambda proxy integration
5. Deploy to stage (e.g., `prod`)

## Environment Configuration

### Set API Base URL
After deployment, update the Lambda function environment variable:

```bash
aws lambda update-function-configuration \
    --function-name pdf-to-pptx-converter \
    --environment Variables='{
        LAMBDA_EXECUTION=true,
        API_BASE_URL=https://your-api-id.execute-api.region.amazonaws.com/prod
    }'
```

## Testing the Deployment

### 1. Health Check
```bash
curl https://your-api-url/
```

### 2. Convert PDF
```bash
curl -X POST "https://your-api-url/convert/pdf-to-pptx" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_path": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
    "output_name": "test_conversion"
  }'
```

### 3. Download Result
Use the returned `pptx_path` URL to download the PowerPoint file.

## Lambda Limitations & Solutions

### File Storage
- ✅ **Lambda `/tmp`**: 10GB temporary storage
- ✅ **Auto cleanup**: Files removed after function execution
- ⚠️ **Persistent storage**: Use S3 for long-term storage if needed

### Memory & Timeout
- ✅ **Memory**: 3008MB (maximum)
- ✅ **Timeout**: 300 seconds (5 minutes)
- ✅ **Sufficient for**: Most PDF conversions

### Package Size
- ✅ **Optimized requirements**: Removed heavy ML libraries
- ✅ **Core functionality**: PDF processing and PowerPoint creation
- ⚠️ **50MB limit**: Deployment package optimized

## API Endpoints

### Production URLs
```
GET  https://your-api-url/
POST https://your-api-url/convert/pdf-to-pptx
GET  https://your-api-url/convert/download-pptx/{filename}
GET  https://your-api-url/convert/list-pptx
POST https://your-api-url/convert/create-sample-pptx
```

## Monitoring

### CloudWatch Logs
```bash
# View logs
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/pdf-to-pptx

# Tail logs
sam logs -n PdfToPptxFunction --tail
```

### Metrics
- Function duration
- Memory utilization  
- Error rates
- Invocation count

## Cost Optimization

### Lambda Pricing
- **Requests**: $0.20 per 1M requests
- **Duration**: $0.0000166667 per GB-second
- **Typical cost**: ~$0.01 per conversion

### Optimization Tips
1. **Concurrent executions**: Limit based on usage
2. **Memory allocation**: 3008MB for performance
3. **Timeout**: 300s for complex PDFs
4. **Reserved concurrency**: Set if needed

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Check Python version compatibility
python --version  # Should be 3.11+
```

#### 2. File Not Found
- Lambda uses `/tmp` directory
- Check file paths in logs

#### 3. Timeout Issues
- Increase timeout to 300 seconds
- Increase memory allocation

#### 4. Package Too Large
- Remove unnecessary dependencies
- Use Lambda layers for common libraries

### Debug Locally
```bash
# Test Lambda function locally
sam local start-api

# Test specific function
sam local invoke PdfToPptxFunction -e events/test-event.json
```

## Security

### IAM Permissions
- ✅ Basic execution role
- ✅ CloudWatch logs access
- ⚠️ Add S3 permissions if using S3 storage

### API Gateway
- ✅ CORS enabled
- ⚠️ Add API keys if needed
- ⚠️ Add rate limiting for production

## Next Steps

1. **Domain Setup**: Use custom domain with Route 53
2. **SSL Certificate**: Use AWS Certificate Manager
3. **CDN**: Add CloudFront for global distribution
4. **Monitoring**: Set up CloudWatch alerts
5. **CI/CD**: Integrate with GitHub Actions

---

🎉 **Your PDF to PowerPoint API is now running on AWS Lambda!**

The serverless architecture provides:
- ✅ **Automatic scaling**
- ✅ **Pay-per-use pricing**
- ✅ **High availability**
- ✅ **No server management**
