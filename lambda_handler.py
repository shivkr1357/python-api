"""
AWS Lambda handler for FastAPI PDF to PowerPoint converter
"""

import os
import json
from mangum import Mangum
from app.main import app

# Configure for Lambda environment
os.environ.setdefault("LAMBDA_EXECUTION", "true")

# Create the Mangum handler
handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    """
    AWS Lambda entry point
    """
    try:
        # Ensure output directories exist
        os.makedirs("/tmp/outputs/pdfs", exist_ok=True)
        os.makedirs("/tmp/outputs/pptx", exist_ok=True)
        
        # Call the Mangum handler
        return handler(event, context)
        
    except Exception as e:
        print(f"Lambda handler error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Internal server error",
                "message": str(e)
            })
        }
